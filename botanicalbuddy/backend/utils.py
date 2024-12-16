import numpy as np
import openai
import os
import logging

logger = logging.getLogger(__name__)

def calculate_cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    magnitude_vec1 = np.linalg.norm(vec1)
    magnitude_vec2 = np.linalg.norm(vec2)
    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0.0
    return dot_product / (magnitude_vec1 * magnitude_vec2)

def get_embedding(text, model="text-embedding-ada-002"):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        logger.error("OPENAI_API_KEY not set. Cannot generate embeddings.")
        return None
    try:
        text = text.replace("\n", " ")
        response = openai.Embedding.create(input=[text], model=model)
        return response["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None