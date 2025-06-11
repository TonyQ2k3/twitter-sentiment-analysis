# A. Installation
The /kubernetes folder contains YAML to deploy all necessary resources.

## 1. Deploy Spark cluster

### 1.1. Build the base image
```bash
cd spark/main/
docker build -t tonyq2k3/spark .
```

### 1.2. Load the image into minikube (if you're using it)
```bash
minikube image load tonyq2k3/spark
```

### 1.3. Run the cluster using Helm
```bash
helm install spark oci://registry-1.docker.io/bitnamicharts/spark -f spark/values.yaml
```

### 1.4. Access the web UI
```bash
kubectl port-forward --namespace default svc/spark-master-svc 80:80
```


## 2. Deploy the crawler server
```bash
kubectl apply -f kubernetes/crawler-server
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

## 5. Deploy Redis
```bash
kubectl create ns redis

helm install redis bitnami/redis -f redis/values.yaml -n redis
```

## 6. Deploy Monitoring (WIP)
Create the monitoring namespace'
```bash
kubectl create namespace monitoring
```

Add Helm Repositories
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

Deploy monitoring
```bash
helm install loki-stack grafana/loki-stack -n monitoring -f monitoring/values.yaml
```

Access the Grafana UI
```bash
kubectl port-forward -n monitoring svc/loki-stack-grafana 8880:80
```

Get the password for `admin`
```bash
kubectl get secret -n monitoring loki-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

All data source should already be configured, so start importing dashboard:
+ `13639`
+ `15757`
+ `15760`

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


/opt/bitnami/spark/bin/spark-submit \
  --class org.apache.spark.examples.SparkPi \
  --packages org.apache.hadoop:hadoop-aws:3.4.1 \
  --master spark://spark-master-0.spark-headless.default.svc.cluster.local:7077 \
  ./test.py
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
