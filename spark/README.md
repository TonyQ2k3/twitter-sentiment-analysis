The codes in /spark folder is used for the submitter containers
Basically, the codes will be containerized into containers that submit the tasks to Apache Spark for 2 purposes:
+ Load a pre-trained model and read data from Kafka to perform sentiment analysis, then save results to database - [/main](/spark/main/)
+ Train and validate a ML model - [/train_validate](/spark/train_validate/)