# Sentiment analysis in brand monitoring using Apache Spark and Kafka

## 👨‍💻 About


## 📁 Repository info
The repo structure is as follows:
+ `/app`: Contains code for a CLI-based Tweet scraper. This tool scrapes data and send to Apache Kafka. It can be containerized to run in K8s.
+ `/docker`: Contains a docker-compose used for early testing. It's useless now so please ignore.
+ `/kubernetes`: Contains YAML files to deploy resources on K8s.
+ `/spark`: Contains codes that serves as "tasks" to submit into Apache Spark. Check the folder's README for more info.