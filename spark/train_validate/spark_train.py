import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
import findspark
findspark.init()
from nltk.corpus import stopwords
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, pandas_udf,col, lower, regexp_replace
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, ArrayType
from pyspark.ml.feature import CountVectorizer, StringIndexer, Tokenizer, StopWordsRemover
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics
from sklearn.metrics import confusion_matrix
from pyspark.ml import PipelineModel, Pipeline, Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param
from pyspark.ml.util import DefaultParamsWritable, DefaultParamsReadable

nltk.download('stopwords')
nltk.download('punkt')

# Define English stopwords
stop_words = stopwords.words('english')


# Create a SparkSession
spark = SparkSession.builder \
    .appName("Text Classification with PySpark") \
    .getOrCreate()
    
    
# Load the data
data = spark.read.csv('data/twitter_training.csv', header=False, inferSchema=True)
validation = spark.read.csv('data/twitter_validation.csv', header=False, inferSchema=True)


# Drop rows with empty 'Text' column
data = data.dropna(subset=['Text'])
validation = validation.dropna(subset=['Text'])


# Define the StringIndexer for the label column (index the labels)
label_indexer = StringIndexer(inputCol="Label", outputCol="Label2")

# Define your index mapping
class_index_mapping = { "Negative": 0, "Positive": 1, "Neutral": 2, "Irrelevant": 3 }

# Fit StringIndexer on data
label_indexer_model = label_indexer.fit(data)
data = label_indexer_model.transform(data)
validation = label_indexer_model.transform(validation)

# Extract label mapping
label_mapping = label_indexer_model.labels

# Print label mapping
print("Label Mapping:")
for index, label in enumerate(label_mapping):
    print(f"Index {index} --> Label '{label}'")
    
    
def clean_text(df, inputCol="Text", outputCol="cleaned_text"):
    # Remove links starting with https://, http://, www., or containing .com
    df = df.withColumn(outputCol, regexp_replace(df[inputCol], r'https?://\S+|www\.\S+|S+\.com\S+|youtu\.be/\S+', ''))
    # Remove words starting with # or @
    df = df.withColumn(outputCol, regexp_replace(df[outputCol], r'(@|#)\w+', ''))
    # Convert text to lowercase
    df = df.withColumn(outputCol, lower(df[outputCol]))
    # Remove non-alpha characters
    df = df.withColumn(outputCol, regexp_replace(df[outputCol], r'[^a-zA-Z\s]', ''))
    
    return df


# Clean the text data
cleaned_data = clean_text(data, inputCol="Text", outputCol="Text")
cleaned_validation = clean_text(validation, inputCol="Text", outputCol="Text")


# Work in progress ....