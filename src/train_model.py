import pandas as pd
import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Load dataset
data_path = "data/resume_dataset.csv"

df = pd.read_csv(data_path)

# Input and output
X = df["resume"]
y = df["job_role"]

# Create AI pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression())
])

# Train model
model.fit(X, y)

# Create models folder
os.makedirs("models", exist_ok=True)

# Save model
joblib.dump(model, "models/resume_model.pkl")

print("Model trained successfully!")
print("Model saved successfully!")