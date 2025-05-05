# The /reddit-crawler folder contains code to build a Crawler that collects Reddit posts

## Register Reddit API credentials
For better details, refer to the [official PRAW API documentation](https://praw.readthedocs.io/en/stable/getting_started/quick_start.html).



## Build the image
```bash
docker build -t tonyq2k3/reddit-crawler:0.2 .
```

## Run the pod
```bash
cd kubernetes

kubectl apply -f ./crawler
```

## Executing CLI
```bash
kubectl exec -it crawler -- /bin/bash

python crawl "Iphone 15" --subs iphone apple

python crawl_kafka "Iphone 15" --subs iphone apple  
```