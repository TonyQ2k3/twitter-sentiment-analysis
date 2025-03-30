from kafka import KafkaProducer
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv() 

# Load CSV data
tweets = pd.read_csv("data/iphone_15_tweets_brief.csv")


# Initialize Kafka producer
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS") or 'host.docker.internal:9092'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))


# Send tweets to Kafka
def send_to_kafka(tweets):
    for index, row in tweets.iterrows():
        tweet_data = {
            'user': str(row['Name']), 
            'tweet': row['Content']
        }
        producer.send('tweets', value=tweet_data)
        producer.flush()
        print("Sent tweet")
    pass
    
    
if __name__ == "__main__":
    send_to_kafka(tweets)