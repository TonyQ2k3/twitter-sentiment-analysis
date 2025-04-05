FROM bde2020/spark-worker:3.2.1-hadoop3.2

# Install Python and pip if not present
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Install Python dependencies
RUN pip3 install kafka-python pymongo nltk

# Download NLTK data
RUN python3 -m nltk.downloader stopwords punkt

# Copy the PySpark consumer script
COPY spark_task.py /app/spark_task.py

WORKDIR /app

ENTRYPOINT ["/spark/bin/spark-submit", "/app/spark_task.py"]
