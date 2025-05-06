The codes in /spark folder is used for the submitter containers
Basically, the codes will be containerized into containers that submit the tasks to Apache Spark for 2 purposes:
+ Load a pre-trained model and read data from Kafka to perform sentiment analysis, then save results to database - [/main](/spark/main/)
+ Train and validate a ML model - [/train_validate](/spark/train_validate/)

## 1. Running the default prediction job
```bash
kubectl exec -it spark-master-0 -- /bin/bash

export MONGO_URI="mongodb://mydatabaseandstuff"

/opt/bitnami/spark/bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 \
 --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
 ./spark_task.py
```

## 2. Running your own job
```bash
# Create a job file called my_task.py and insert your custom task
touch my_task.py

# Copy it into the master pod
kubectl cp my_task.py default/spark-master-0:/app

# Run the job
kubectl exec -it spark-master-0 -- /bin/bash

/opt/bitnami/spark/bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 \
 --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
 ./spark_task.py
```

