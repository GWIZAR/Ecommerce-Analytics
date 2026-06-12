import json
import os
import csv
from datetime import datetime

# Simulate HBase wide-column store using Python dictionaries
# Row key: user_id + timestamp (for sessions)
# Row key: product_id + date (for product metrics)

print("=" * 60)
print("HBase Wide-Column Store Simulation")
print("=" * 60)

# Load data
with open("data/sessions_0.json") as f:
    sessions = json.load(f)
with open("data/sessions_1.json") as f:
    sessions += json.load(f)

with open("data/products.json") as f:
    products = json.load(f)

# ── TABLE 1: user_sessions ──
# Row key: user_id + reverse_timestamp
# Column families: session_info, device, behavior
print("\nCreating HBase table: user_sessions")
print("Column families: session_info, device, behavior")
print("-" * 60)

user_sessions_table = {}
for s in sessions:
    # Row key = user_id + reverse timestamp (for recent-first ordering)
    ts = datetime.fromisoformat(s["start_time"])
    reverse_ts = 9999999999 - int(ts.timestamp())
    row_key = f"{s['user_id']}_{reverse_ts}"

    user_sessions_table[row_key] = {
        # Column family: session_info
        "session_info:session_id": s["session_id"],
        "session_info:start_time": s["start_time"],
        "session_info:duration_seconds": str(s["duration_seconds"]),
        "session_info:conversion_status": s["conversion_status"],
        "session_info:referrer": s["referrer"],
        # Column family: device
        "device:type": s["device_profile"]["type"],
        "device:os": s["device_profile"]["os"],
        "device:browser": s["device_profile"]["browser"],
        # Column family: behavior
        "behavior:viewed_products": str(len(s["viewed_products"])),
        "behavior:page_views": str(len(s["page_views"])),
        "behavior:cart_items": str(len(s["cart_contents"])),
        "behavior:city": s["geo_data"]["city"],
    }

print(f"Inserted {len(user_sessions_table)} rows into user_sessions table")

# ── TABLE 2: product_metrics ──
# Row key: product_id + date
# Column families: views, cart, sales
print("\nCreating HBase table: product_metrics")
print("Column families: views, cart, sales")
print("-" * 60)

product_metrics_table = {}
for s in sessions:
    date = s["start_time"][:10]
    for prod_id in s["viewed_products"]:
        row_key = f"{prod_id}_{date}"
        if row_key not in product_metrics_table:
            product_metrics_table[row_key] = {
                "views:count": 0,
                "cart:count": 0,
                "sales:count": 0,
                "sales:revenue": 0.0
            }
        product_metrics_table[row_key]["views:count"] += 1
        if prod_id in s["cart_contents"]:
            product_metrics_table[row_key]["cart:count"] += 1

print(f"Inserted {len(product_metrics_table)} rows into product_metrics table")

# ── QUERY 1: Get all sessions for a specific user ──
print("\n" + "=" * 60)
print("QUERY 1: Get sessions for user_000001")
print("=" * 60)
target_user = "user_000001"
user_rows = {k: v for k, v in user_sessions_table.items() if k.startswith(target_user)}
print(f"Found {len(user_rows)} sessions for {target_user}:")
for row_key, cols in list(user_rows.items())[:3]:
    print(f"  Row: {row_key}")
    print(f"    session_info:start_time = {cols['session_info:start_time']}")
    print(f"    session_info:conversion_status = {cols['session_info:conversion_status']}")
    print(f"    device:type = {cols['device:type']}")
    print(f"    behavior:viewed_products = {cols['behavior:viewed_products']}")

# ── QUERY 2: Get product metrics for a specific product ──
print("\n" + "=" * 60)
print("QUERY 2: Product view metrics for prod_00001")
print("=" * 60)
target_prod = "prod_00001"
prod_rows = {k: v for k, v in product_metrics_table.items() if k.startswith(target_prod)}
print(f"Found {len(prod_rows)} daily records for {target_prod}:")
for row_key, cols in list(sorted(prod_rows.items()))[:5]:
    print(f"  Row: {row_key}")
    print(f"    views:count = {cols['views:count']}")
    print(f"    cart:count = {cols['cart:count']}")

# ── QUERY 3: Scan sessions by device type ──
print("\n" + "=" * 60)
print("QUERY 3: Session count by device type")
print("=" * 60)
device_counts = {}
for cols in user_sessions_table.values():
    device = cols["device:type"]
    device_counts[device] = device_counts.get(device, 0) + 1
for device, count in sorted(device_counts.items(), key=lambda x: -x[1]):
    print(f"  {device}: {count} sessions")

# ── QUERY 4: Conversion rate scan ──
print("\n" + "=" * 60)
print("QUERY 4: Conversion status distribution")
print("=" * 60)
conversion_counts = {}
for cols in user_sessions_table.values():
    status = cols["session_info:conversion_status"]
    conversion_counts[status] = conversion_counts.get(status, 0) + 1
for status, count in sorted(conversion_counts.items(), key=lambda x: -x[1]):
    pct = count / len(user_sessions_table) * 100
    print(f"  {status}: {count} ({pct:.1f}%)")

# Save tables to CSV for report
os.makedirs("hbase_output", exist_ok=True)
with open("hbase_output/user_sessions_sample.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["row_key", "session_id", "start_time", "device_type", "conversion_status", "viewed_products"])
    for row_key, cols in list(user_sessions_table.items())[:20]:
        writer.writerow([row_key, cols["session_info:session_id"], cols["session_info:start_time"],
                        cols["device:type"], cols["session_info:conversion_status"], cols["behavior:viewed_products"]])

print("\nHBase simulation complete!")
print("Sample data saved to hbase_output/")
