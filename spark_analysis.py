from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import warnings
warnings.filterwarnings("ignore")

spark = SparkSession.builder \
    .appName("EcommerceAnalytics") \
    .master("local[*]") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

print("=" * 60)
print("Apache Spark E-Commerce Analytics")
print("=" * 60)

# Load Data
print("\nLoading data...")
transactions_df = spark.read.option("multiline","true").json("data/transactions.json")
users_df = spark.read.option("multiline","true").json("data/users.json")
products_df = spark.read.option("multiline","true").json("data/products.json")
sessions_df = spark.read.option("multiline","true").json("data/sessions_*.json")

print(f"  Transactions: {transactions_df.count()}")
print(f"  Users: {users_df.count()}")
print(f"  Products: {products_df.count()}")
print(f"  Sessions: {sessions_df.count()}")

# BATCH JOB 1: Data Cleaning
print("\n" + "=" * 60)
print("BATCH JOB 1: Data Cleaning & Normalization")
print("=" * 60)

transactions_clean = transactions_df \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withColumn("date", to_date(col("timestamp"))) \
    .withColumn("hour", hour(col("timestamp"))) \
    .withColumn("month", month(col("timestamp"))) \
    .filter(col("total") > 0)

sessions_clean = sessions_df \
    .withColumn("start_time", to_timestamp(col("start_time"))) \
    .withColumn("end_time", to_timestamp(col("end_time")))

print(f"  Clean transactions: {transactions_clean.count()}")
print(f"  Clean sessions: {sessions_clean.count()}")

# BATCH JOB 2: Co-Purchase Analysis
print("\n" + "=" * 60)
print("BATCH JOB 2: Product Co-Purchase Analysis")
print("=" * 60)

items_df = transactions_clean.select("transaction_id", "user_id", explode("items").alias("item"))
items_df = items_df.select("transaction_id", "user_id", col("item.product_id").alias("product_id"))

co_purchase = items_df.alias("a").join(
    items_df.alias("b"),
    (col("a.transaction_id") == col("b.transaction_id")) &
    (col("a.product_id") < col("b.product_id"))
).groupBy(
    col("a.product_id").alias("product_1"),
    col("b.product_id").alias("product_2")
).count().withColumnRenamed("count", "times_bought_together") \
 .orderBy(desc("times_bought_together"))

print("Top 10 co-purchased product pairs:")
co_purchase.show(10, truncate=False)

# SPARK SQL
print("=" * 60)
print("SPARK SQL ANALYTICS")
print("=" * 60)

transactions_clean.createOrReplaceTempView("transactions")
users_df.createOrReplaceTempView("users")
products_df.createOrReplaceTempView("products")
sessions_clean.createOrReplaceTempView("sessions")

print("\nSQL Query 1: Daily Revenue Trend (Top 10)")
spark.sql("""
    SELECT date,
        COUNT(*) as transactions,
        ROUND(SUM(total), 2) as revenue,
        ROUND(AVG(total), 2) as avg_order
    FROM transactions
    GROUP BY date
    ORDER BY revenue DESC
    LIMIT 10
""").show()

print("SQL Query 2: Payment Method Performance")
spark.sql("""
    SELECT payment_method,
        COUNT(*) as transactions,
        ROUND(SUM(total), 2) as total_revenue,
        ROUND(AVG(total), 2) as avg_order,
        ROUND(AVG(discount), 2) as avg_discount
    FROM transactions
    GROUP BY payment_method
    ORDER BY total_revenue DESC
""").show()

print("SQL Query 3: Transaction Status Breakdown")
spark.sql("""
    SELECT status,
        COUNT(*) as count,
        ROUND(SUM(total), 2) as revenue,
        ROUND(AVG(total), 2) as avg_value
    FROM transactions
    GROUP BY status
    ORDER BY count DESC
""").show()

print("SQL Query 4: Hourly Sales Pattern")
spark.sql("""
    SELECT hour,
        COUNT(*) as transactions,
        ROUND(SUM(total), 2) as revenue
    FROM transactions
    GROUP BY hour
    ORDER BY hour
""").show(24)

print("Spark analysis complete!")
spark.stop()
