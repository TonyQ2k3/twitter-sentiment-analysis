# This is a server that users can make requests to have it crawl data for them
It's built based on the code in [reddit-crawler](../reddit-crawler)


```bash
curl -X POST http://localhost:8090/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "tesla",
    "subreddits": ["technology", "cars"],
    "limit": 5,
    "time_filter": "week"
}'
```