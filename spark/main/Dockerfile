# Use OpenJDK as base
FROM openjdk:11-jre-slim

# Install Python and basic tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install PySpark + dependencies
RUN pip3 install pyspark findspark pymongo nltk kafka-python python-dotenv setuptools

WORKDIR /app

COPY . /app

# Install Python dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# Start container in interactive shell mode
CMD ["tail", "-f", "/dev/null"]