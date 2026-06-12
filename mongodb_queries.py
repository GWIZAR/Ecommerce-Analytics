from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

print("=" * 60)
print("AGGREGATION 1: Top 10 Best-Selling Products")
print("=" * 60)
pipeline1 = [
    {"$unwind": "$items"},
    {"$group": {
        "_id": "$items.product_id",
        "total_quantity_sold": {"$sum": "$items.quantity"},
        "total_revenue": {"$sum": "$items.subtotal"},
        "num_transactions": {"$sum": 1}
    }},
    {"$sort": {"total_quantity_sold": -1}},
    {"$limit": 10}
]
results = list(db.transactions.aggregate(pipeline1))
for r in results:
    print(f"  Product: {r['_id']} | Qty Sold: {r['total_quantity_sold']} | Revenue: ${r['total_revenue']:.2f}")

print("\n" + "=" * 60)
print("AGGREGATION 2: Revenue by Payment Method")
print("=" * 60)
pipeline2 = [
    {"$group": {
        "_id": "$payment_method",
        "total_revenue": {"$sum": "$total"},
        "num_transactions": {"$sum": 1},
        "avg_order_value": {"$avg": "$total"}
    }},
    {"$sort": {"total_revenue": -1}}
]
results = list(db.transactions.aggregate(pipeline2))
for r in results:
    print(f"  {r['_id']} | Revenue: ${r['total_revenue']:.2f} | Transactions: {r['num_transactions']} | Avg: ${r['avg_order_value']:.2f}")

print("\n" + "=" * 60)
print("AGGREGATION 3: User Segmentation by Age Group")
print("=" * 60)
pipeline3 = [
    {"$bucket": {
        "groupBy": "$age",
        "boundaries": [18, 25, 35, 45, 55, 70],
        "default": "Other",
        "output": {
            "count": {"$sum": 1},
            "avg_age": {"$avg": "$age"}
        }
    }}
]
results = list(db.users.aggregate(pipeline3))
age_labels = {18: "18-24", 25: "25-34", 35: "35-44", 45: "45-54", 55: "55-69"}
for r in results:
    label = age_labels.get(r['_id'], str(r['_id']))
    print(f"  Age Group {label}: {r['count']} users")

print("\n" + "=" * 60)
print("AGGREGATION 4: Top 5 Categories by Revenue")
print("=" * 60)
pipeline4 = [
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
        "total_revenue": {"$sum": "$items.subtotal"},
        "items_sold": {"$sum": "$items.quantity"}
    }},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 5}
]
results = list(db.transactions.aggregate(pipeline4))
for r in results:
    print(f"  Category: {r['_id']} | Revenue: ${r['total_revenue']:.2f} | Items Sold: {r['items_sold']}")

print("\n" + "=" * 60)
print("AGGREGATION 5: Conversion Rate by Referrer")
print("=" * 60)
pipeline5 = [
    {"$group": {
        "_id": "$referrer",
        "total_sessions": {"$sum": 1},
        "converted": {"$sum": {"$cond": [{"$eq": ["$conversion_status", "converted"]}, 1, 0]}}
    }},
    {"$project": {
        "total_sessions": 1,
        "converted": 1,
        "conversion_rate": {"$multiply": [{"$divide": ["$converted", "$total_sessions"]}, 100]}
    }},
    {"$sort": {"conversion_rate": -1}}
]
results = list(db.sessions.aggregate(pipeline5))
for r in results:
    print(f"  {r['_id']} | Sessions: {r['total_sessions']} | Converted: {r['converted']} | Rate: {r['conversion_rate']:.1f}%")

print("\nDone!")
client.close()
