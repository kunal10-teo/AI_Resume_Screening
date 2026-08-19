from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load semantic AI model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def semantic_match(resume_text, job_description):

    if not resume_text or not job_description:
        return 0.0

    resume_embedding = model.encode(
        [resume_text]
    )

    job_embedding = model.encode(
        [job_description]
    )

    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    score = similarity * 100

    return round(score, 2)