import praw
import argparse
import time

def create_reddit_instance():
    return praw.Reddit(
        client_id="my client id",
        client_secret="my client secret",
        password="my password",
        user_agent="my user agent",
        username="my username",
    )

def search_reddit_posts(reddit, keywords, limit=10):
    results = []
    
    for keyword in keywords:
        print(f"Searching for: {keyword}")
        
        # Crawl posts using the keyword during the last 7 days
        submissions = reddit.subreddit('all').search(query=keyword, limit=limit, sort='new', time_filter='week')
        
        for submission in submissions:
            results.append({
                'author': submission.author.name if submission.author else 'N/A',
                'title': submission.title,
                'created': submission.created_utc
            })
            if len(results) >= limit:
                break
    return results

def display_results(results):
    for result in results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Score: {result['score']}")
        print(f"Author: {result['author']}")
        print(f"Created: {result['created']}")
        print('-' * 80)


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