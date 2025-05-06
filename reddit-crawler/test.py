import pandas as pd


df = pd.read_csv('posts/Switch 2_2025-05-05_22-40-47.csv')
print(df.iloc[0]['Title'])