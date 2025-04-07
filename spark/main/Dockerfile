FROM bitnami/spark:3.5.5-debian-12-r2

WORKDIR /app

COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start container in interactive shell mode
CMD ["tail", "-f", "/dev/null"]

# Alternatively, you can uncomment the following line to run the script directly
# ENTRYPOINT ["/spark/bin/spark-submit", "/app/spark_task.py"]