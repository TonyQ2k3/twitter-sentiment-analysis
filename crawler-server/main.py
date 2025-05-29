from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import os
import sys
import datetime
import re
import json
from kafka import KafkaProducer
import praw
from dotenv import load_dotenv
import uvicorn

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Failed to load .env: {e}")
    sys.exit(1)

# Kafka producer setup
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", 'kafka-svc.default.svc.cluster.local')
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# FastAPI app
app = FastAPI()
portNumber = os.getenv("PORT", 8090)

# Allowed time filters
TimeFilter = Literal["all", "day", "hour", "month", "week", "year"]

# Request model
class CrawlRequest(BaseModel):
    keyword: str
    subreddits: Optional[List[str]] = Field(default=["gadgets"])
    limit: Optional[int] = Field(default=10, gt=0)
    time_filter: Optional[TimeFilter] = Field(default="month")


def create_reddit_instance():
    return praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        username=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        user_agent=os.getenv("USER_AGENT"),
    )


def is_relevant(text):
    url_pattern = r'https?://\S+|www\.\S+'
    emoji_pattern = r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FAFF]'
    gif_pattern = r'!\[gif\]'
    deleted_pattern = r'\[deleted\]'
    combined_pattern = f'({url_pattern}|{emoji_pattern}|{gif_pattern}|{deleted_pattern})'
    return not bool(re.search(combined_pattern, text))


def crawl_reddit_data(keyword: str, subreddits: List[str], limit: int, time_filter: str):
    reddit = create_reddit_instance()
    count = 0
    for subreddit in subreddits:
        submissions = reddit.subreddit(subreddit).search(query=keyword, limit=limit, time_filter=time_filter)
        for submission in submissions:
            if not is_relevant(submission.title):
                continue
            created_date = datetime.datetime.fromtimestamp(submission.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
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

            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                if not is_relevant(comment.body):
                    continue
                comment_date = datetime.datetime.fromtimestamp(comment.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                comment_data = {
                    'product': keyword,
                    'text': comment.body,
                    'author': comment.author.name if comment.author else 'N/A',
                    'score': comment.score,
                    'created': comment_date
                }
                producer.send('reddits', value=comment_data)
                producer.flush()
                count += 1
    print(f"Sent {count} items to Kafka topic: reddits")


@app.post("/crawl")
def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    if not request.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    background_tasks.add_task(
        crawl_reddit_data,
        keyword=request.keyword,
        subreddits=request.subreddits,
        limit=request.limit,
        time_filter=request.time_filter
    )
    return {
        "message": f"Crawl started for '{request.keyword}' in subreddits {request.subreddits} with time filter '{request.time_filter}'"
    }
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=portNumber)