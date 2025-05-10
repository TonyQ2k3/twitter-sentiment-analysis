import praw
import argparse
import os
import datetime
import sys
import pandas as pd
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
    
    
def is_relevant(text):
    url_pattern = r'https?://\S+|www\.\S+'
    emoji_pattern = r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]|[\U0001F800-\U0001F8FF]|[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FAFF]'
    gif_pattern = r'!\[gif\]'
    deleted_pattern = r'\[deleted\]'
    # Combine patterns for filtering
    combined_pattern = f'({url_pattern}|{emoji_pattern}|{gif_pattern}|{deleted_pattern})'
    
    return not bool(re.search(combined_pattern, text))


def search_reddit_posts(reddit, keyword, subreddits=['gadgets'], limit=10):
    if subreddits is None or len(subreddits) == 0:
        subreddits = ['gadgets']
        
    results = []
    
    for subreddit in subreddits:
        print(f"Searching in subreddit: {subreddit}")
        print(f"Searching for: {keyword}")
        
        # Crawl posts using the keyword during the last 7 days
        submissions = reddit.subreddit(subreddit).search(query=keyword, limit=limit, time_filter='month')
        
        for submission in submissions:
            if not is_relevant(submission.title):
                continue
            created_date = datetime.datetime.fromtimestamp(submission.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            results.append({
                'author': submission.author.name if submission.author else 'N/A',
                'title': submission.title,
                'score': submission.score,
                'created': created_date
            })
            
            # Load all comments for the post
            submission.comments.replace_more(limit=None)
            for comment in submission.comments.list():
                if not is_relevant(comment.body):
                    continue
                comment_date = datetime.datetime.fromtimestamp(comment.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                results.append({
                    'author': comment.author.name if comment.author else 'N/A',
                    'title': comment.body,
                    'score': comment.score,
                    'created': comment_date
                })
    return results


def save_to_csv(results, topic="General"):
    print("Saving posts to CSV...")
    now = datetime.datetime.now()
    folder_path = "./posts/"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("Created Folder: {}".format(folder_path))
        
    df = pd.DataFrame(results)
    df.columns = ['Author', 'Title', 'Score', 'Date']
    
    df['Product'] = topic

    current_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"{folder_path}{topic}_{current_time}.csv"
    pd.set_option("display.max_colwidth", None)
    df.to_csv(file_path, index=False, encoding="utf-8")

    print("CSV Saved: {}".format(file_path))
    pass


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
    results = search_reddit_posts(reddit, args.query, args.subs, args.limit)
    
    # Check if results are empty
    if len(results) == 0:
        print("No results found.")
        return
    else:
        print(f"Found {len(results)} results.")
        save_to_csv(results, args.query)


if __name__ == '__main__':
    main()