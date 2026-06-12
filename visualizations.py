import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

os_import = __import__('os')
os_import.makedirs("charts", exist_ok=True)

sns.set_theme(style="darkgrid")
print("Generating visualizations...")

# ── CHART 1: Revenue by Payment Method ──
print("  Chart 1: Revenue by Payment Method")
pipeline = [{"$group": {"_id": "$payment_method", "revenue": {"$sum": "$total"}, "count": {"$sum": 1}}},
            {"$sort": {"revenue": -1}}]
data = list(db.transactions.aggregate(pipeline))
methods = [d["_id"] for d in data]
revenues = [d["revenue"] for d in data]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(methods, revenues, color=sns.color_palette("Blues_d", len(methods)))
ax.set_title("Total Revenue by Payment Method", fontsize=14, fontweight='bold')
ax.set_xlabel("Payment Method")
ax.set_ylabel("Total Revenue ($)")
for bar, val in zip(bars, revenues):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
            f"${val:,.0f}", ha='center', fontsize=9)
plt.tight_layout()
plt.savefig("charts/revenue_by_payment.png", dpi=150)
plt.close()

# ── CHART 2: User Age Distribution ──
print("  Chart 2: User Age Distribution")
users = list(db.users.find({}, {"age": 1, "_id": 0}))
ages = [u["age"] for u in users if "age" in u]

fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(ages, bins=15, color="#2196F3", edgecolor="white", alpha=0.85)
ax.set_title("User Age Distribution", fontsize=14, fontweight='bold')
ax.set_xlabel("Age")
ax.set_ylabel("Number of Users")
plt.tight_layout()
plt.savefig("charts/user_age_distribution.png", dpi=150)
plt.close()

# ── CHART 3: Top 10 Best-Selling Products ──
print("  Chart 3: Top 10 Best-Selling Products")
pipeline = [
    {"$unwind": "$items"},
    {"$group": {"_id": "$items.product_id", "qty": {"$sum": "$items.quantity"}, "revenue": {"$sum": "$items.subtotal"}}},
    {"$sort": {"qty": -1}},
    {"$limit": 10}
]
data = list(db.transactions.aggregate(pipeline))
prods = [d["_id"] for d in data]
qtys = [d["qty"] for d in data]

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=qtys, y=prods, palette="viridis", ax=ax)
ax.set_title("Top 10 Best-Selling Products by Quantity", fontsize=14, fontweight='bold')
ax.set_xlabel("Units Sold")
ax.set_ylabel("Product ID")
plt.tight_layout()
plt.savefig("charts/top_products.png", dpi=150)
plt.close()

# ── CHART 4: Conversion Rate by Referrer ──
print("  Chart 4: Conversion Rate by Referrer")
pipeline = [
    {"$group": {
        "_id": "$referrer",
        "total": {"$sum": 1},
        "converted": {"$sum": {"$cond": [{"$eq": ["$conversion_status", "converted"]}, 1, 0]}}
    }},
    {"$project": {"rate": {"$multiply": [{"$divide": ["$converted", "$total"]}, 100]}}},
    {"$sort": {"rate": -1}}
]
data = list(db.sessions.aggregate(pipeline))
referrers = [d["_id"] for d in data]
rates = [d["rate"] for d in data]

fig, ax = plt.subplots(figsize=(8, 5))
colors = sns.color_palette("RdYlGn", len(referrers))
bars = ax.barh(referrers, rates, color=colors)
ax.set_title("Conversion Rate by Traffic Source", fontsize=14, fontweight='bold')
ax.set_xlabel("Conversion Rate (%)")
for bar, val in zip(bars, rates):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va='center', fontsize=9)
plt.tight_layout()
plt.savefig("charts/conversion_by_referrer.png", dpi=150)
plt.close()

# ── CHART 5: Daily Revenue Trend ──
print("  Chart 5: Daily Revenue Trend")
with open("data/transactions.json") as f:
    txns = json.load(f)

daily = defaultdict(float)
for t in txns:
    date = t["timestamp"][:10]
    daily[date] += t["total"]

dates = sorted(daily.keys())
revenues = [daily[d] for d in dates]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, revenues, color="#2196F3", linewidth=1.5)
ax.fill_between(range(len(dates)), revenues, alpha=0.2, color="#2196F3")
ax.set_xticks(range(0, len(dates), 7))
ax.set_xticklabels([dates[i] for i in range(0, len(dates), 7)], rotation=45, fontsize=8)
ax.set_title("Daily Revenue Trend", fontsize=14, fontweight='bold')
ax.set_xlabel("Date")
ax.set_ylabel("Revenue ($)")
plt.tight_layout()
plt.savefig("charts/daily_revenue_trend.png", dpi=150)
plt.close()

# ── CHART 6: Transaction Status Pie ──
print("  Chart 6: Transaction Status Distribution")
pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
data = list(db.transactions.aggregate(pipeline))
labels = [d["_id"] for d in data]
counts = [d["count"] for d in data]

fig, ax = plt.subplots(figsize=(7, 7))
ax.pie(counts, labels=labels, autopct='%1.1f%%',
       colors=sns.color_palette("Set2", len(labels)), startangle=90)
ax.set_title("Transaction Status Distribution", fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig("charts/transaction_status.png", dpi=150)
plt.close()

print("\nAll charts saved to charts/ folder!")
client.close()
