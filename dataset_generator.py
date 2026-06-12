import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_USERS = 500
NUM_CATEGORIES = 20
NUM_PRODUCTS = 500
NUM_SESSIONS = 2000
NUM_TRANSACTIONS = 1000
DAYS = 90
START_DATE = datetime(2025, 1, 1)

print("Generating categories...")
categories = []
for i in range(NUM_CATEGORIES):
    cat_id = f"cat_{i:03d}"
    num_subs = random.randint(2, 5)
    subcategories = []
    for j in range(num_subs):
        subcategories.append({
            "subcategory_id": f"sub_{i:03d}_{j:02d}",
            "name": fake.bs().title(),
            "profit_margin": round(random.uniform(0.10, 0.40), 2)
        })
    categories.append({
        "category_id": cat_id,
        "name": fake.company(),
        "subcategories": subcategories
    })

with open(f"{OUTPUT_DIR}/categories.json", "w") as f:
    json.dump(categories, f, indent=2)
print(f"  Generated {len(categories)} categories")

print("Generating users...")
users = []
for i in range(NUM_USERS):
    reg_date = START_DATE - timedelta(days=random.randint(30, 365))
    last_active = START_DATE + timedelta(days=random.randint(0, DAYS))
    users.append({
        "user_id": f"user_{i:06d}",
        "name": fake.name(),
        "email": fake.email(),
        "age": random.randint(18, 70),
        "gender": random.choice(["M", "F", "Other"]),
        "geo_data": {
            "city": fake.city(),
            "state": fake.state_abbr(),
            "country": "US"
        },
        "registration_date": reg_date.isoformat(),
        "last_active": last_active.isoformat(),
        "preferred_categories": random.sample([c["category_id"] for c in categories], k=random.randint(1, 4))
    })

with open(f"{OUTPUT_DIR}/users.json", "w") as f:
    json.dump(users, f, indent=2)
print(f"  Generated {len(users)} users")

print("Generating products...")
products = []
for i in range(NUM_PRODUCTS):
    cat = random.choice(categories)
    sub = random.choice(cat["subcategories"])
    base_price = round(random.uniform(5.99, 499.99), 2)
    creation_date = START_DATE - timedelta(days=random.randint(0, 180))
    price_history = []
    price = round(base_price * random.uniform(0.8, 1.2), 2)
    for _ in range(random.randint(1, 3)):
        price_history.append({
            "price": price,
            "date": (creation_date + timedelta(days=random.randint(0, 60))).isoformat()
        })
        price = round(price * random.uniform(0.9, 1.1), 2)
    price_history.append({"price": base_price, "date": (START_DATE + timedelta(days=random.randint(0, 30))).isoformat()})

    products.append({
        "product_id": f"prod_{i:05d}",
        "name": fake.catch_phrase().title(),
        "category_id": cat["category_id"],
        "subcategory_id": sub["subcategory_id"],
        "base_price": base_price,
        "current_stock": random.randint(0, 200),
        "is_active": random.random() > 0.1,
        "price_history": price_history,
        "creation_date": creation_date.isoformat(),
        "rating": round(random.uniform(1.0, 5.0), 1),
        "review_count": random.randint(0, 500)
    })

with open(f"{OUTPUT_DIR}/products.json", "w") as f:
    json.dump(products, f, indent=2)
print(f"  Generated {len(products)} products")

print("Generating sessions...")
product_ids = [p["product_id"] for p in products]
user_ids = [u["user_id"] for u in users]
category_ids = [c["category_id"] for c in categories]

sessions = []
for i in range(NUM_SESSIONS):
    user_id = random.choice(user_ids)
    start_time = START_DATE + timedelta(
        days=random.randint(0, DAYS),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    duration = random.randint(60, 3600)
    end_time = start_time + timedelta(seconds=duration)
    viewed = random.sample(product_ids, k=random.randint(1, 8))
    page_views = []
    t = start_time
    page_views.append({"timestamp": t.isoformat(), "page_type": "home", "product_id": None, "category_id": None, "view_duration": random.randint(10, 120)})
    for prod_id in viewed:
        t += timedelta(seconds=random.randint(30, 300))
        cat_id = next((p["category_id"] for p in products if p["product_id"] == prod_id), None)
        page_views.append({"timestamp": t.isoformat(), "page_type": "product_detail", "product_id": prod_id, "category_id": cat_id, "view_duration": random.randint(30, 300)})

    cart = {}
    for prod_id in random.sample(viewed, k=random.randint(0, min(3, len(viewed)))):
        price = next((p["base_price"] for p in products if p["product_id"] == prod_id), 9.99)
        cart[prod_id] = {"quantity": random.randint(1, 3), "price": price}

    conversion = "converted" if cart and random.random() > 0.4 else ("abandoned_cart" if cart else "browsed")

    sessions.append({
        "session_id": f"sess_{fake.lexify('??????????')}",
        "user_id": user_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration,
        "geo_data": {
            "city": fake.city(),
            "state": fake.state_abbr(),
            "country": "US",
            "ip_address": fake.ipv4()
        },
        "device_profile": {
            "type": random.choice(["mobile", "desktop", "tablet"]),
            "os": random.choice(["iOS", "Android", "Windows", "macOS"]),
            "browser": random.choice(["Chrome", "Safari", "Firefox", "Edge"])
        },
        "viewed_products": viewed,
        "page_views": page_views,
        "cart_contents": cart,
        "conversion_status": conversion,
        "referrer": random.choice(["search_engine", "direct", "social_media", "email", "referral"])
    })

# Split sessions into multiple files
chunk_size = 500
for idx, chunk_start in enumerate(range(0, len(sessions), chunk_size)):
    chunk = sessions[chunk_start:chunk_start + chunk_size]
    with open(f"{OUTPUT_DIR}/sessions_{idx}.json", "w") as f:
        json.dump(chunk, f, indent=2)
print(f"  Generated {len(sessions)} sessions in {idx+1} files")

print("Generating transactions...")
transactions = []
converted_sessions = [s for s in sessions if s["conversion_status"] == "converted" and s["cart_contents"]]

for i, session in enumerate(converted_sessions[:NUM_TRANSACTIONS]):
    items = []
    subtotal = 0
    for prod_id, cart_item in session["cart_contents"].items():
        line_subtotal = round(cart_item["price"] * cart_item["quantity"], 2)
        subtotal += line_subtotal
        items.append({
            "product_id": prod_id,
            "quantity": cart_item["quantity"],
            "unit_price": cart_item["price"],
            "subtotal": line_subtotal
        })
    subtotal = round(subtotal, 2)
    discount = round(subtotal * random.uniform(0, 0.15), 2) if random.random() > 0.6 else 0.0
    total = round(subtotal - discount, 2)

    transactions.append({
        "transaction_id": f"txn_{fake.lexify('????????????')}",
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "timestamp": session["end_time"],
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "payment_method": random.choice(["credit_card", "paypal", "debit_card", "crypto"]),
        "status": random.choice(["completed", "shipped", "delivered", "returned"])
    })

with open(f"{OUTPUT_DIR}/transactions.json", "w") as f:
    json.dump(transactions, f, indent=2)
print(f"  Generated {len(transactions)} transactions")

print("\nDataset generation complete!")
print(f"Files saved in '{OUTPUT_DIR}/' folder:")
for fname in os.listdir(OUTPUT_DIR):
    size = os.path.getsize(f"{OUTPUT_DIR}/{fname}")
    print(f"  {fname}: {size/1024:.1f} KB")
