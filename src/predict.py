import joblib

# Load trained model
model = joblib.load("models/resume_model.pkl")

# Test resume
resume_text = """
Python, SQL, Machine Learning, Pandas, Numpy,
Data Analysis and Artificial Intelligence skills
"""

# Prediction
prediction = model.predict([resume_text])

print("Recommended Job Role:", prediction[0])