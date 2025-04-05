from kafka import KafkaProducer
import os
import sys
import argparse
import getpass
import pandas as pd
import json
from tweets_scraper import Twitter_Scraper

try:
    from dotenv import load_dotenv
    print("Loading environment vars")
    load_dotenv()
    print("Loaded environment vars\n")
except Exception as e:
    print(f"Error loading environment vars: {e}")
    sys.exit(1)
    
    
def not_real_tweets():
    # Initialize Kafka producer
    bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS") or 'host.docker.internal:9092'
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    tweets = pd.read_csv("data/twitter_validation.csv")
    
    for index, row in tweets.iterrows():
        tweet_data = {
            'product': str(row['Product']),
            'tweet': row['Text']
        }
        producer.send('tweets', value=tweet_data)
        producer.flush()
        print(f"Sent tweet #{index}")
    print("Sent tweets")


def main():
    try:
        parser = argparse.ArgumentParser(
            add_help=True,
            usage="python scraper [option] ... [arg] ...",
            description="Twitter Scraper - Scrape tweets from Twitter profiles, hashtags, and bookmarks.",
        )

        try:
            parser.add_argument(
                "--user",
                type=str,
                default=os.getenv("USER_UNAME"),
            )
            parser.add_argument(
                "--password",
                type=str,
                default=os.getenv("USER_PASSWORD"),
            )
        except Exception as e:
            print(f"Error retrieving environment variables: {e}")
            sys.exit(1)
            
        # Real mode
        parser.add_argument(
            "--real",
            action="store_true",
            help="Real tweets will be scraped. If false (default), tweets will be sent from a csv file.",
        )

        # Number of tweets
        parser.add_argument(
            "-t",
            "--tweets",
            type=int,
            default=50,
            help="Number of tweets to scrape (default: 50)",
        )

        # Target username
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            default=None,
            help="Twitter username. Scrape tweets from a user's profile.",
        )

        # Target hashtag
        parser.add_argument(
            "-ht",
            "--hashtag",
            type=str,
            default=None,
            help="Twitter hashtag. Scrape tweets from a hashtag.",
        )
        parser.add_argument(
            "-ntl",
            "--no_tweets_limit",
            nargs='?',
            default=False,
            help="Set no limit to the number of tweets to scrape (will scrap until no more tweets are available).",
        )

        parser.add_argument(
            "-q",
            "--query",
            type=str,
            default=None,
            help="Twitter query or search. Scrape tweets from a query or search.",
        )

        parser.add_argument(
            "--latest",
            action="store_true",
            help="Scrape latest tweets",
        )

        parser.add_argument(
            "--top",
            action="store_true",
            help="Scrape top tweets",
        )

        args = parser.parse_args()
        
        # Check if --real is set to False
        if args.real is False:
            print("Sending NOT real tweets")
            not_real_tweets()
            sys.exit(0)

        USER_UNAME = args.user
        USER_PASSWORD = args.password

        if USER_UNAME is None:
            USER_UNAME = input("Twitter Username: ")

        if USER_PASSWORD is None:
            USER_PASSWORD = getpass.getpass("Enter Password: ")

        print()

        tweet_type_args = []

        if args.username is not None:
            tweet_type_args.append(args.username)
        if args.hashtag is not None:
            tweet_type_args.append(args.hashtag)
        if args.query is not None:
            tweet_type_args.append(args.query)

        if len(tweet_type_args) > 1:
            print("Specify only one of --username, --hashtag, or --query.")
            sys.exit(1)

        # Check if only one of the arguments is provided
        if args.latest and args.top:
            print("Sspecify either --latest or --top. Not both.")
            sys.exit(1)

        if USER_UNAME is not None and USER_PASSWORD is not None:
            scraper = Twitter_Scraper(
                username=USER_UNAME,
                password=USER_PASSWORD
            )
            scraper.login()
            scraper.scrape_tweets(
                max_tweets=args.tweets,
                no_tweets_limit= args.no_tweets_limit if args.no_tweets_limit is not None else True,
                scrape_username=args.username,
                scrape_hashtag=args.hashtag,
                scrape_query=args.query,
                scrape_latest=args.latest,
                scrape_top=args.top
            )
            scraper.save_to_csv()
            if not scraper.interrupted:
                scraper.driver.close()
        else:
            print(
                "Missing Twitter username or password environment variables. Please check your .env file."
            )
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nScript Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(1)


if __name__ == "__main__":
    main()
