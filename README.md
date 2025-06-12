# Sentiment analysis in brand monitoring using Apache Spark and Kafka
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)


## 👨‍💻 About
This is the repo for deploying sentiment analysis using Kafka, Spark and Kubernetes.

## 📑 Workflow diagram
![Workflow Diagram](docs/KLTN_App.drawio.png)
+ **Dashboard Application**: The app that users interact with
+ **Sentiment Analyzer**: Handles on-demand sentiment analysis of products
+ **Database**: Stores and caches data
+ **Monitoring (WIP)**: Monitor cluster performance

## 📁 Repository info
The repo structure is as follows:
+ `/kubernetes`: Contains YAML files to deploy resources on K8s. Those includes:
    - `crawler-server`
    - `kafka`
    - `spark`
    - `redis`
    - `dashboard`
+ `/spark`: Contains codes that serves as "tasks" to submit into Apache Spark. Check the folder's README for more info.

Deploy cluster:
```bash
aws eks update-kubeconfig --name devops-eks-cluster --region us-east-1
```