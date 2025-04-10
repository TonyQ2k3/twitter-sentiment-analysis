The codes in /spark folder is used for the submitter containers
Basically, the codes will be containerized into containers that submit the tasks to Apache Spark for 2 purposes:
+ Load a pre-trained model and read data from Kafka to perform sentiment analysis, then save results to database - [/main](/spark/main/)
+ Train and validate a ML model - [/train_validate](/spark/train_validate/)

```bash
/opt/bitnami/spark/bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
 ./spark_nomaster.py
```

```
helm install spark oci://registry-1.docker.io/bitnamicharts/spark
  --set image.repository=tonyq2k3/task-submitter
  --set image.tag=0.4
  --set image.pullPolicy=Never
  --set global.security.allowInsecureImages=true
  --set master.containerSecurityContext.readOnlyRootFilesystem=false
  --set worker.containerSecurityContext.readOnlyRootFilesystem=false


export MONGO_URI="blah"
export BOOTSTRAP_SERVERS="kafka-svc.default.svc.cluster.local"
```

