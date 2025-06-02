import mlflow
import os
 
mlflow.set_tracking_uri("https://dagshub.com/TranChucThien/kltn-sentiment-monitoring-mlops.mlflow")
model_uri = os.getenv("MODEL_URI") or "models:/CountVectorizer_Model/1"
local_model_path = "./model"
 
# Download once on the driver
print("Downloading model to driver...")
model_dir = mlflow.artifacts.download_artifacts(model_uri, dst_path=local_model_path)
print(f"Driver model path: {model_dir}")