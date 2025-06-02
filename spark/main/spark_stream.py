import os
import sys
import re
from pymongo import MongoClient
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, udf, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

import mlflow
import mlflow.spark
from dotenv import load_dotenv

# Load environment variables
try:
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")
    sys.exit(1)

# MongoDB setup
try:
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    database = client["main"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

class_index_mapping = {0: "Negative", 1: "Positive", 2: "Neutral"}

schema = StructType([
    StructField("product", StringType(), True),
    StructField("requester_id", StringType(), True),
    StructField("text", StringType(), True),
    StructField("author", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("created", StringType(), True)
])


def load_model_from_mlflow(model_uri):
    """
    Load a model from MLflow.
    :param model_uri: URI of the model in MLflow.
    :return: Loaded model.
    """
    model = mlflow.spark.load_model(model_uri)
    return model


def clean_text(text):
    if text is not None:
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FAFF]', '', text)
        text = re.sub(r'!\[gif\]', '', text)
        text = re.sub(r'\[deleted\]', '', text)
        text = re.sub(r'(@|#)\w+', '', text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    else:
        return ''


if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName("Kafka Pyspark Streaming") \
        .getOrCreate()

    # Load from local path on driver (and workers, since model exists now)
    print("Loading model from local path...")
    local_model_path = "./model"
    pipeline = mlflow.spark.load_model(local_model_path)

    @udf(StringType())
    def clean_text_udf(text):
        return clean_text(text)

    def process_batch(batch_df, batch_id):
        if batch_df.isEmpty():
            return

        parsed_df = batch_df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*") \
            .withColumn("original", col("text")) \
            .withColumn("Text", clean_text_udf(col("text")))

        processed_df = pipeline.transform(parsed_df)

        results = processed_df.select("product", "requester_id", "author", "original", "score", "created", "prediction")
        for row in results.collect():
            reddit_doc = {
                "product": row.product,
                "text": row.original,
                "author": row.author,
                "score": row.score,
                "created": row.created,
                "prediction": class_index_mapping[int(row.prediction)]
            }
            collection_name = f"reddits_{row.requester_id}"
            collection = database[collection_name]
            collection.insert_one(reddit_doc)

    df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-svc.default.svc.cluster.local:9092") \
        .option("subscribe", "reddits") \
        .load()

    query = df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()
