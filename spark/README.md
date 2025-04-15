The codes in /spark folder is used for the submitter containers
Basically, the codes will be containerized into containers that submit the tasks to Apache Spark for 2 purposes:
+ Load a pre-trained model and read data from Kafka to perform sentiment analysis, then save results to database - [/main](/spark/main/)
+ Train and validate a ML model - [/train_validate](/spark/train_validate/)

```bash
/opt/bitnami/spark/bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 \
 --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
 ./spark_task.py
```

