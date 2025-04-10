from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("Example PySpark Code") \
    .getOrCreate()

# Create a sample DataFrame
data = [("Alice", 1), ("Bob", 2), ("Cathy", 3)]
columns = ["Name", "Id"]

df = spark.createDataFrame(data, columns)

# Show the original DataFrame
print("Original DataFrame:")
df.show()
