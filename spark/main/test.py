import os
import sys
import re
from pymongo import MongoClient
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, udf, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.ml import PipelineModel

import mlflow
import mlflow.spark
from dotenv import load_dotenv

# Initialize SparkSession with S3A support
spark = SparkSession.builder \
    .appName("WordCountToMinIO") \
    .getOrCreate()

# Configure MinIO S3 endpoint and credentials
hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.endpoint", "http://minio.default.svc.cluster.local:9000")
hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")
hadoop_conf.set("fs.s3a.fast.upload", "true")
hadoop_conf.set("fs.s3a.access.key", "admin")
hadoop_conf.set("fs.s3a.secret.key", "password")
hadoop_conf.set("fs.s3a.path.style.access", "true")
hadoop_conf.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")


# Sample data
lines = spark.sparkContext.parallelize([
    "hello world",
    "hello spark",
    "hello minio"
])

# Word count logic
words = lines.flatMap(lambda line: line.split(" "))
word_pairs = words.map(lambda word: (word, 1))
word_counts = word_pairs.reduceByKey(lambda a, b: a + b)

# Convert to DataFrame
df = word_counts.toDF(["word", "count"])

# Write to MinIO in CSV format
df.printSchema()

df.write.format("csv").option("header", "true").save("s3a://spark-data/word_counts.csv")

print("✅ Job completed and written to MinIO!")

spark.stop()