# The /app folder contains the code to build a Twitter scraper
This app is meant to run inside a pod of a K8s cluster. If you run it as a stand-alone container, it will crash.


## Build the image
```bash
cd app

docker build -t scrape-producer .
```

## Run the pod
```bash
cd kubernetes

kubectl apply -f ./scraper
```

## Access the tool's CLI
Rename `scraper_secret.yaml.example` to `scraper_secret.yaml` and edit USER_UNAME and USER_PASSWORD according to your twitter account.

To access the scraper's CLI, run:
```bash
kubectl exec -it scraper -- /bin/bash
```

## Usage
To run the tool for testing, use this command to read tweets from a file:
```bash
python scraper
```
If you want to the tool to actually scrape data (it doesn't work right now), run:
```bash
python scraper --real
```
