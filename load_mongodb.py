import json
import os
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]

DATA_DIR = "data"

# Load categories
print("Loading categories...")
with open(f"{DATA_DIR}/categories.json") as f:
    data = json.load(f)
db.categories.drop()
db.categories.insert_many(data)
print(f"  Inserted {len(data)} categories")

# Load users
print("Loading users...")
with open(f"{DATA_DIR}/users.json") as f:
    data = json.load(f)
db.users.drop()
db.users.insert_many(data)
print(f"  Inserted {len(data)} users")

# Load products
print("Loading products...")
with open(f"{DATA_DIR}/products.json") as f:
    data = json.load(f)
db.products.drop()
db.products.insert_many(data)
print(f"  Inserted {len(data)} products")

# Load sessions
print("Loading sessions...")
db.sessions.drop()
total_sessions = 0
for i in range(4):
    fname = f"{DATA_DIR}/sessions_{i}.json"
    if os.path.exists(fname):
        with open(fname) as f:
            data = json.load(f)
        db.sessions.insert_many(data)
        total_sessions += len(data)
print(f"  Inserted {total_sessions} sessions")

# Load transactions
print("Loading transactions...")
with open(f"{DATA_DIR}/transactions.json") as f:
    data = json.load(f)
db.transactions.drop()
db.transactions.insert_many(data)
print(f"  Inserted {len(data)} transactions")

print("\nAll data loaded into MongoDB successfully!")
print("Collections:")
for col in db.list_collection_names():
    print(f"  {col}: {db[col].count_documents({})} documents")

client.close()
