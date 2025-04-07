The codes in /spark folder is used for the submitter containers
Basically, the codes will be containerized into containers that submit the tasks to Apache Spark for 2 purposes:
+ Load a pre-trained model and read data from Kafka to perform sentiment analysis, then save results to database - [/main](/spark/main/)
+ Train and validate a ML model - [/train_validate](/spark/train_validate/)

spark-submit --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 --name pyspark-job --conf spark.executor.instances=2 --conf spark.kubernetes.container.image=bitnami/spark:3.5.5-debian-12-r2 local:///app/spark_task.py

spark-submit \
    --class org.apache.spark.examples.SparkPi \
    --conf spark.kubernetes.container.image=bitnami/spark:3.5.5-debian-12-r2 \
    --master k8s://https://k8s-apiserver-host:k8s-apiserver-port \
    --conf spark.kubernetes.driverEnv.SPARK_MASTER_URL=spark://spark-master-svc:7077 \
    --deploy-mode cluster \
    ./examples/jars/spark-examples_2.12-3.2.0.jar 1000