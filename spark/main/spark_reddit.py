import os
import sys
import re
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, udf, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql.types import *

import mlflow
import mlflow.spark
from dotenv import load_dotenv
 
try:
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")
    sys.exit(1)
 
# Create a new client and connect to the server
# Establish connection to MongoDB - database name: main, collection name: tweets
try:
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    database = client["main"]
    print("Connected to MongoDB: ", uri)
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)
 
class_index_mapping = { 0: "Negative", 1: "Positive", 2: "Neutral" }

 
schema = StructType([
    StructField("product", StringType(), True),
    StructField("requester_id", StringType(), True),
    StructField("text", StringType(), True),
    StructField("author", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("created", StringType(), True)
])
 
# Load the model
# pipeline = PipelineModel.load("logistic_regression_model.pkl")

def load_model_from_mlflow(model_uri):
    """
    Load a model from MLflow.
    :param model_uri: URI of the model in MLflow.
    :return: Loaded model.
    """
    # Load the model
    model = mlflow.spark.load_model(model_uri)
    return model

# Clean tweets and remove unwanted characters
def clean_text(text):
    if text is not None:
        # Remove any URLs and irrelevant characters
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FAFF]', '', text)
        text = re.sub(r'!\[gif\]', '', text)
        text = re.sub(r'\[deleted\]', '', text)
       
        # Remove tag-words starting with # or @
        text = re.sub(r'(@|#)\w+', '', text)
       
        # Convert to lowercase
        text = text.lower()
       
        # Remove non-alphanumeric characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
       
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    else:
        return ''


if __name__ == "__main__":
    mlflow.set_tracking_uri("https://dagshub.com/TranChucThien/kltn-sentiment-monitoring-mlops.mlflow")
    
    spark = SparkSession.builder \
        .appName("Kafka Pyspark Streaming") \
        .getOrCreate()

    # Load from Dagshub
    model_uri = os.getenv("MODEL_URI", "models:/reddit-sentiment-analysis/Production")
    pipeline = mlflow.spark.load_model(model_uri)
    
    # Kafka consumer setup
    df = spark.read.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-svc.default.svc.cluster.local:9092") \
        .option("subscribe", "reddits") \
        .load()
    
    # Parse the JSON string in the value column
    json_df = df.selectExpr("CAST(value AS STRING)")
    
    # Convert JSON string to DataFrame with the defined schema
    parsed_df = json_df.select(from_json(col("value"), schema).alias("data")) \
                    .select("data.*") \
                    .withColumn("original", col("text"))


    # Clean tweets and remove unwanted characters
    cleaned_df = parsed_df.withColumn("Text", udf(clean_text)(col("text")))
    cleaned_df.printSchema()  


    # Run the model
    processed_df = pipeline.transform(cleaned_df)
    processed_df.printSchema()
    
    # Make a new dataframe with the predictions
    predictions = processed_df.select("product", "requester_id", "author", "original", "score", "created", "prediction").collect()
    
    # Send to MongoDB

    for row in predictions:
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
    spark.stop()
    