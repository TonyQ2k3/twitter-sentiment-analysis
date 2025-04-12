import os
import sys
import re
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import PipelineModel
 
try:
    from dotenv import load_dotenv
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
    collection = database["tweets"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)
 
 
spark = SparkSession.builder \
    .appName("Kafka Pyspark Streaming") \
    .getOrCreate()
    
spark.sparkContext.setLogLevel("ERROR")
 
schema = StructType([
    StructField("product", StringType(), True),
    StructField("text", StringType(), True)
])
 
# Load the model
pipeline = PipelineModel.load("logistic_regression_model.pkl")
 
# Clean tweets and remove unwanted characters
def clean_text(text):
    if text is not None:
        # Remove any URLs
        text = re.sub(r'https?://\S+|www\.\S+|\.com\S+|youtu\.be/\S+', '', text)
       
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
   
class_index_mapping = { 0: "Negative", 1: "Positive", 2: "Neutral", 3: "Irrelevant" }
 
 
# Kafka consumer setup
df = spark.read.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-svc.default.svc.cluster.local:9092") \
    .option("subscribe", "tweets") \
    .load()
 
# Parse the JSON string in the value column
json_df = df.selectExpr("CAST(value AS STRING)")
json_df.printSchema()
 
# Convert JSON string to DataFrame with the defined schema
parsed_df = json_df.select(from_json(col("value"), schema).alias("data")) \
                   .select("data.*")

# Clean tweets and remove unwanted characters
cleaned_df = parsed_df.withColumn("Text", udf(clean_text)(col("text")))

# Run the model
processed_df = pipeline.transform(cleaned_df)
 
# Make a new dataframe with the predictions
predictions = processed_df.select("product", "text", "Text", "prediction").collect()

# Send to MongoDB
for row in predictions:
    tweet_doc = {
        "product": row.product,
        "text": row.text,
        "prediction": class_index_mapping[int(row.prediction)]
    }
    collection.insert_one(tweet_doc)
 
spark.stop()