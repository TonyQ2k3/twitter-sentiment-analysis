## Deploy Kafka
```bash
kubectl apply -f kafka
```

## Deploy Kafkacat (to check Kafka)
```bash
kubectl apply -f kafkacat
kubectl exec -it kafkacat -- /bin/sh

# List all topics
kafkacat -b $KAFKA_BROKER -L

# Consume tweets from a topic
kafkacat -b $KAFKA_BROKER -t tweets -C
```