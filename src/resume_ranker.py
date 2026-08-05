from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_score(resume_text, job_description):

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(documents)

    score = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )

    return round(score[0][0] * 100, 2)



resume = """
Python SQL Machine Learning Pandas
Data Analysis Artificial Intelligence
"""

job = """
Looking for Data Scientist with Python,
SQL, Machine Learning and Data Analysis skills
"""


result = calculate_score(resume, job)

print("Resume Match Score:", result, "%")