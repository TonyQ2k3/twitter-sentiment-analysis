import praw
import argparse
import os
import datetime
import sys

# Load .env variables from .env file
try:
    from dotenv import load_dotenv
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")
    sys.exit(1)


def create_reddit_instance():
    return praw.Reddit(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        user_agent=os.getenv("USER_AGENT"),
    )

def search_reddit_posts(reddit, keywords, limit=10):
    results = []
    
    for keyword in keywords:
        print(f"Searching for: {keyword}")
        
        # Crawl posts using the keyword during the last 7 days
        submissions = reddit.subreddit('all').search(query=keyword, limit=limit, sort='new', time_filter='week')
        
        for submission in submissions:
            created_date = datetime.datetime.fromtimestamp(submission.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            results.append({
                'author': submission.author.name if submission.author else 'N/A',
                'title': submission.title,
                'created': created_date
            })
    return results

def display_results(results):
    for result in results:
        print(f"Author: {result['author']}")
        print(f"Title: {result['title']}")
        print(f"Created: {result['created']}")
        print('-' * 20)


def main():
    parser = argparse.ArgumentParser(description='Monitor brand mentions on Reddit.')
    parser.add_argument('--query', nargs='+', help='Keywords to search for')
    parser.add_argument('--limit', type=int, default=10, help='Number of posts to fetch per keyword')
    
    args = parser.parse_args()
    
    reddit = create_reddit_instance()
    results = search_reddit_posts(reddit, args.query, args.limit)
    display_results(results)


if __name__ == '__main__':
    main()