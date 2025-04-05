from pyspark.ml import PipelineModel
import re
import nltk
from kafka import KafkaConsumer
from json import loads
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


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
spark = SparkSession.builder \
    .appName("Kafka Pyspark Streaming") \
    .master("spark://spark-master-svc.default.svc.cluster.local:7077") \
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
consumer = KafkaConsumer(
    'tweets',
    bootstrap_servers='kafka-svc.default.svc.cluster.local:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='tweets-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

# Process messages from Kafka
for message in consumer:
    tweet = message.value[-1]  # get the Text from the list
    preprocessed_tweet = clean_text(tweet)
    
    # Create a DataFrame from the string
    data = [(preprocessed_tweet,),]  
    data = spark.createDataFrame(data, ["Text"])
    
    # Apply the pipeline to transform the DataFrame
    processed_tweets = pipeline.transform(data)
    prediction = processed_tweets.collect()[0][6]

    print("-> Tweet:", tweet)
    print("-> preprocessed_tweet : ", preprocessed_tweet)
    print("-> Predicted Sentiment:", prediction)
    print("-> Predicted Sentiment classname:", class_index_mapping[int(prediction)])


# Work in progress ....