import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

models = [
    SentenceTransformer("all-MiniLM-L6-v2"),  # 384-dim
    SentenceTransformer("all-mpnet-base-v2"),  # 768-dim
]

TARGET_DIM = 512

def get_combined_embedding(text):

    if not text.strip():
        return np.zeros(TARGET_DIM)  

    embeddings = [model.encode(text, convert_to_numpy=True) for model in models]
    resized_embeddings = [np.resize(embed, TARGET_DIM) for embed in embeddings]

    return np.mean(resized_embeddings, axis=0)  # Compute mean embedding


BIAS_KEYWORDS = {
    "Left": [
        "wealth inequality", "progressive taxation", "social justice", "universal healthcare",
        "climate action", "gun control", "labor rights", "racial equity", "LGBTQ+ rights",
        "higher minimum wage", "government regulation", "corporate accountability",
        "free college", "environmental justice", "social safety nets"
    ],
    "Right": [
        "free market capitalism", "tax cuts", "individual responsibility", "limited government",
        "border security", "strong national defense", "gun rights", "religious freedom",
        "lower corporate taxes", "traditional family values", "economic deregulation",
        "school choice", "law and order", "energy independence", "personal liberty"
    ],
}

# Compute bias embeddings using keyword sets
bias_embeddings = {
    bias: get_combined_embedding(" ".join(keywords)) for bias, keywords in BIAS_KEYWORDS.items()
}

def get_bias_score(content, threshold=0.6):

    if not content.strip():
        return 0.5  

    content_embedding = get_combined_embedding(content)

    similarities = {
        bias: cosine_similarity(content_embedding.reshape(1, -1), embedding.reshape(1, -1))[0][0]
        for bias, embedding in bias_embeddings.items()
    }

    max_sim = max(similarities.values())

    # If similarity is below threshold, return 0.5 (neutral)
    return round(max_sim, 2) if max_sim >= threshold else 0.5


