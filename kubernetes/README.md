# A. Installation
The /kubernetes folder contains YAML to deploy all necessary resources.

## 1. Deploy Spark cluster

### 1.1. Build the base image
```bash
cd spark/main/
docker build -t tonyq2k3/task-submitter:0.4 .
```

### 1.2. Load the image into minikube (if you're using it)
```bash
minikube image load tonyq2k3/task-submitter:0.4
```

### 1.3. Run the cluster using Helm
```bash
helm install spark oci://registry-1.docker.io/bitnamicharts/spark \
  --set image.repository=tonyq2k3/task-submitter \
  --set image.tag=0.4 \
  --set image.pullPolicy=Always \
  --set worker.replicaCount=3
  --set global.security.allowInsecureImages=true \
  --set master.containerSecurityContext.readOnlyRootFilesystem=false \
  --set worker.containerSecurityContext.readOnlyRootFilesystem=false \
```
or
```bash
helm install spark oci://registry-1.docker.io/bitnamicharts/spark -f spark/values.yaml
```

### 1.4. Access the web UI
```bash
kubectl port-forward --namespace default svc/spark-master-svc 80:80
```


## 2. Deploy the scraper
For more information on what commands to run inside the app container, check the README in [/app/](/app/)
```bash
kubectl apply -f kubernetes/scraper
```


## 3. Deploy Kafka and Zookeeper
```bash
kubectl apply -f kubernetes/kafka
```


## 4. Deploy Kafkacat (to check Kafka and topics)
```bash
kubectl apply -f kafkacat
kubectl exec -it kafkacat -- /bin/sh

# List all topics
kafkacat -b $KAFKA_BROKER -L

# Consume tweets from a topic
kafkacat -b $KAFKA_BROKER -t reddits -C
```


-----------------------------------------------------------
# B. Submitting a job 

## 1. Running the default prediction job
```bash
kubectl exec -it spark-master-0 -- /bin/bash

export MONGO_URI="mongodb://mydatabaseandstuff"

/opt/bitnami/spark/bin/spark-submit \
 --class org.apache.spark.examples.SparkPi \
 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5 \
 --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
 ./spark_reddit.py
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
 ./my_task.py
```