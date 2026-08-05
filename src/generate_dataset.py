import pandas as pd
import os

data = {
    "resume": [
        "Python SQL Machine Learning Pandas Numpy Data Analysis",
        "Java Spring Boot HTML CSS JavaScript Developer",
        "Python Machine Learning Deep Learning AI Data Scientist",
        "SQL Excel PowerBI Data Analyst",
        "C++ Java Algorithms Software Engineer"
    ],
    "job_role": [
        "Data Scientist",
        "Web Developer",
        "AI Engineer",
        "Data Analyst",
        "Software Engineer"
    ]
}

df = pd.DataFrame(data)

os.makedirs("../data", exist_ok=True)

df.to_csv("data/resume_dataset.csv", index=False)
print("Dataset generated successfully!")