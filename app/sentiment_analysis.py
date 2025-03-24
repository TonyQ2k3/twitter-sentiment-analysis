from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from textblob import TextBlob

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Kafka to CSV with Sentiment Analysis") \
    .getOrCreate()

# Define UDF for sentiment analysis
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

sentiment_udf = udf(analyze_sentiment, StringType())

# Read from Kafka
df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "tweets") \
    .load()

# Process the data
tweets_df = df.selectExpr("CAST(value AS STRING) as tweet")

# Analyze sentiment
result_df = tweets_df.withColumn("sentiment", sentiment_udf(col("tweet")))

# Write results to Cassandra
result_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="sentiment_results", keyspace="your_keyspace") \
    .mode("append") \
    .save()

spark.stop()