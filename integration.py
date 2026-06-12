import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

print("=" * 60)
print("PART 3: Integrated Analytics")
print("=" * 60)

# ── INTEGRATION 1: Customer Lifetime Value (CLV) ──
print("\nINTEGRATION 1: Customer Lifetime Value Estimation")
print("-" * 60)
print("Business Question: Who are our most valuable customers?")
print("Data Sources: MongoDB (users + transactions) + HBase (sessions)")
print()

# From MongoDB: Get total spend per user
pipeline = [
    {"$group": {
        "_id": "$user_id",
        "total_spent": {"$sum": "$total"},
        "num_orders": {"$sum": 1},
        "avg_order": {"$avg": "$total"}
    }},
    {"$sort": {"total_spent": -1}},
    {"$limit": 10}
]
clv_data = list(db.transactions.aggregate(pipeline))

# From HBase simulation: Get session engagement per user
with open("data/sessions_0.json") as f:
    sessions = json.load(f)
with open("data/sessions_1.json") as f:
    sessions += json.load(f)

session_engagement = defaultdict(lambda: {"sessions": 0, "total_duration": 0, "conversions": 0})
for s in sessions:
    uid = s["user_id"]
    session_engagement[uid]["sessions"] += 1
    session_engagement[uid]["total_duration"] += s["duration_seconds"]
    if s["conversion_status"] == "converted":
        session_engagement[uid]["conversions"] += 1

print(f"{'User ID':<15} {'Total Spent':>12} {'Orders':>8} {'Sessions':>10} {'CLV Score':>10}")
print("-" * 60)
for d in clv_data:
    uid = d["_id"]
    eng = session_engagement.get(uid, {"sessions": 0, "total_duration": 0, "conversions": 0})
    # CLV Score = total_spent * (1 + conversion_rate)
    conv_rate = eng["conversions"] / max(eng["sessions"], 1)
    clv_score = d["total_spent"] * (1 + conv_rate)
    print(f"{uid:<15} ${d['total_spent']:>11,.2f} {d['num_orders']:>8} {eng['sessions']:>10} ${clv_score:>9,.2f}")

# ── INTEGRATION 2: Funnel Conversion Analysis ──
print("\n\nINTEGRATION 2: Purchase Funnel Analysis")
print("-" * 60)
print("Business Question: Where do users drop off in the purchase funnel?")
print("Data Sources: HBase (browsing sessions) + MongoDB (transactions)")
print()

total_sessions = len(sessions)
sessions_with_views = sum(1 for s in sessions if len(s.get("viewed_products", [])) > 0)
sessions_with_cart = sum(1 for s in sessions if len(s.get("cart_contents", {})) > 0)
sessions_converted = sum(1 for s in sessions if s["conversion_status"] == "converted")
total_transactions = db.transactions.count_documents({})

print(f"  Stage 1 - Total Sessions:        {total_sessions:>6}")
print(f"  Stage 2 - Viewed Products:       {sessions_with_views:>6} ({sessions_with_views/total_sessions*100:.1f}%)")
print(f"  Stage 3 - Added to Cart:         {sessions_with_cart:>6} ({sessions_with_cart/total_sessions*100:.1f}%)")
print(f"  Stage 4 - Converted (Session):   {sessions_converted:>6} ({sessions_converted/total_sessions*100:.1f}%)")
print(f"  Stage 5 - Completed Transaction: {total_transactions:>6} ({total_transactions/total_sessions*100:.1f}%)")

# Funnel chart
stages = ["Sessions", "Viewed\nProducts", "Added\nto Cart", "Converted", "Transactions"]
values = [total_sessions, sessions_with_views, sessions_with_cart, sessions_converted, total_transactions]

fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#1565C0", "#1976D2", "#1E88E5", "#42A5F5", "#90CAF9"]
bars = ax.bar(stages, values, color=colors, width=0.5)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            str(val), ha='center', fontweight='bold')
ax.set_title("Purchase Funnel Analysis\n(MongoDB + HBase Integration)", fontsize=14, fontweight='bold')
ax.set_ylabel("Number of Users/Sessions")
plt.tight_layout()
plt.savefig("charts/funnel_analysis.png", dpi=150)
plt.close()
print("\n  Funnel chart saved!")

# ── INTEGRATION 3: Product Affinity by Category ──
print("\n\nINTEGRATION 3: Product Affinity by Category")
print("-" * 60)
print("Business Question: Which categories drive the most revenue?")
print("Data Sources: MongoDB (transactions + products)")
print()

pipeline = [
    {"$unwind": "$items"},
    {"$lookup": {
        "from": "products",
        "localField": "items.product_id",
        "foreignField": "product_id",
        "as": "product"
    }},
    {"$unwind": "$product"},
    {"$group": {
        "_id": "$product.category_id",
        "revenue": {"$sum": "$items.subtotal"},
        "units": {"$sum": "$items.quantity"},
        "transactions": {"$sum": 1}
    }},
    {"$sort": {"revenue": -1}},
    {"$limit": 10}
]
cat_data = list(db.transactions.aggregate(pipeline))

print(f"{'Category':<12} {'Revenue':>12} {'Units':>8} {'Transactions':>14}")
print("-" * 50)
for d in cat_data:
    print(f"{d['_id']:<12} ${d['revenue']:>11,.2f} {d['units']:>8} {d['transactions']:>14}")

# Category revenue chart
fig, ax = plt.subplots(figsize=(10, 5))
cats = [d["_id"] for d in cat_data]
revs = [d["revenue"] for d in cat_data]
sns.barplot(x=cats, y=revs, palette="Blues_d", ax=ax, hue=cats, legend=False)
ax.set_title("Revenue by Product Category\n(Integrated Query)", fontsize=14, fontweight='bold')
ax.set_xlabel("Category")
ax.set_ylabel("Revenue ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("charts/category_revenue.png", dpi=150)
plt.close()
print("\n  Category chart saved!")

print("\n\nIntegration analysis complete!")
client.close()
