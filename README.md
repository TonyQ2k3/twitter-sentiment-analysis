# Sentiment analysis in brand monitoring using Apache Spark and Kafka
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)


## 👨‍💻 About
This is the repo for deploying sentiment analysis using Kafka, Spark and Kubernetes.

## 📑 Workflow diagram
![Workflow Diagram](docs/diagram.png)
+ **Tweet scraper**: Collect tweets from Twitter and send (produce) them to Kafka.
+ **Kafka data broker**: Store tweets in topic.
+ **Spark cluster**: Read (consume) tweets from Kafka topic, load pre-trained model, run sentiment analysis and save result to a database.
+ **MongoDB database**: Store sentiment results
+ **Sentiment visualization**: Read data from database, aggregate them and visualize via web app.
+ **End-user**: Search for a product (e.g Iphone 15) and see visualization.

## 📁 Repository info
The repo structure is as follows:
+ `/app`: Contains code for a CLI-based Tweet scraper. This tool scrapes data and send to Apache Kafka. It can be containerized to run in K8s.
+ `/kubernetes`: Contains YAML files to deploy resources on K8s.
+ `/spark`: Contains codes that serves as "tasks" to submit into Apache Spark. Check the folder's README for more info.