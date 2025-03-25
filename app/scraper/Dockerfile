FROM python:3.13.2

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# Run the application
CMD ["python", "tweets_scraper.py"]