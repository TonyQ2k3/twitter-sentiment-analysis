import os
import sys
import re
import nltk
from kafka import KafkaConsumer
from json import loads
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
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
# Establish connection to MongoDB
try:
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    database = client["main"]
    collection = database["tweets"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

# Only download if not already present (safe for containerized environments)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


# Setup Spark session
spark_master = os.getenv("SPARK_MASTER") or "spark://spark-master-svc.default.svc.cluster.local:7077"
spark = SparkSession.builder \
    .appName("Kafka Pyspark Streaming") \
    .master(spark_master) \
    .getOrCreate()
    
spark.sparkContext.setLogLevel("ERROR")


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
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS") or 'host.docker.internal:9092'
consumer = KafkaConsumer(
    'tweets',
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='tweets-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

# Process messages from Kafka
for message in consumer:
    product = message.value[0]  # get the product from the list
    text = message.value[-1]  # get the text from the list
    preprocessed_tweet = clean_text(text)
    
    # Create a DataFrame from the string
    data = [(preprocessed_tweet,),]  
    data = spark.createDataFrame(data, ["Text"])
    
    # Apply the pipeline to transform the DataFrame
    processed_tweets = pipeline.transform(data)
    prediction = processed_tweets.collect()[0][6]
    
    print("-> Tweet:", text)
    # print("-> preprocessed_tweet : ", preprocessed_tweet)
    # print("-> Predicted Sentiment:", prediction)
    print("-> Predicted Sentiment classname:", class_index_mapping[int(prediction)])

    tweet_doc = {
        "product": product,
        "text": text,
        "prediction": class_index_mapping[int(prediction)]
    }

    # Insert document into MongoDB collection
    collection.insert_one(tweet_doc)


    
# Work in progress ....
