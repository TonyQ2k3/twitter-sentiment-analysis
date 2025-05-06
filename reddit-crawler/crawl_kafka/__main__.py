from kafka import KafkaProducer
import praw
import argparse
import os
import datetime
import sys
import json
import re

# Load .env variables from .env file
try:
    from dotenv import load_dotenv
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")
    sys.exit(1)
    
    
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS") or 'kafka-svc.default.svc.cluster.local'
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'))


def create_reddit_instance():
    print(
        os.getenv("CLIENT_ID"),
        os.getenv("CLIENT_SECRET"),
        os.getenv("USER"),
        os.getenv("PASSWORD")
    )
    return praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        username=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        user_agent=os.getenv("USER_AGENT"),
    )
    

def is_relevant(submission):
    url_pattern = r'https?://\S+|www\.\S+'
    emoji_pattern = r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FAFF]'
    gif_pattern = r'!\[gif\]'
    deleted_pattern = r'\[deleted\]'
    # Combine patterns for filtering
    combined_pattern = f'({url_pattern}|{emoji_pattern}|{gif_pattern}|{deleted_pattern})'
    
    return not bool(re.search(combined_pattern, submission.title))
    

def search_reddit_posts(reddit, keyword, subreddits=['gadgets'], limit=10):  
    count = 0
    if subreddits is None or len(subreddits) == 0:
        subreddits = ['gadgets']
    
    for subreddit in subreddits:
        print(f"Searching in subreddit: {subreddit}")
        print(f"Searching for: {keyword}")
        
        # Crawl posts using the keyword during the last 7 days
        submissions = reddit.subreddit(subreddit).search(query=keyword, limit=limit, time_filter='month')
        
        for submission in submissions:
            if not is_relevant(submission):
                continue
            created_date = datetime.datetime.fromtimestamp(submission.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            # Send the post data to Kafka
            post_data = {
                'product': keyword,
                'text': submission.title,
                'author': submission.author.name if submission.author else 'N/A',
                'score': submission.score,
                'created': created_date
            }
            producer.send('reddits', value=post_data)
            producer.flush()
            count += 1
            
            # Load all comments
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                # Send the comment data to Kafka
                comment_data = {
                    'product': keyword,
                    'text': comment.body,
                    'author': comment.author.name if comment.author else 'N/A',
                    'score': comment.score,
                    'created': created_date
                }
                producer.send('reddits', value=comment_data)
                producer.flush()
                count += 1
                
        print(f"Sent {count} posts to Kafka topic: reddits")



def main():
    parser = argparse.ArgumentParser(description='Monitor brand mentions on Reddit.')
    parser.add_argument('query', type=str, help='Keywords to search for')
    parser.add_argument('--subs', nargs='+', help='Subreddits to search in')
    parser.add_argument('--limit', type=int, default=10, help='Number of posts to fetch per keyword')
    args = parser.parse_args()
    
    # Check if the user provided a query
    if not args.query.strip():
        parser.error("Keyword cannot be empty. Please provide a valid search keyword.")

    reddit = create_reddit_instance()
    search_reddit_posts(reddit, args.query, args.subs, args.limit)


if __name__ == '__main__':
    main()