from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load AI model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def semantic_similarity(resume, job):

    embeddings = model.encode(
        [
            resume,
            job
        ]
    )

    score = cosine_similarity(
        [
            embeddings[0]
        ],
        [
            embeddings[1]
        ]
    )[0][0]


    return round(score * 100, 2)