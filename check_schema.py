from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Schema").master("local[*]").config("spark.driver.memory","2g").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
transactions_df = spark.read.option("multiline","true").json("data/transactions.json")
print("Transaction schema:")
transactions_df.printSchema()
transactions_df.show(2, truncate=False)
spark.stop()
