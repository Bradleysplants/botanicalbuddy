import openai
import os
from openai import AsyncOpenAI
import logging
import numpy as np

logger=logging.getLogger(__name__)
async def get_embedding(text, model="text-embedding-ada-002"):
    """
    Asynchronously generates an OpenAI embedding for a given text, using the specified model.

    Args:
        text (str): The text to generate an embedding for.
        model (str, optional): The model to use. Defaults to "text-embedding-ada-002".

    Returns:
        list: The embedding as a list of floats.
    """
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        client = AsyncOpenAI()
        response = await client.embeddings.create(input=[text], model=model)
        return response["data"][0]["embedding"]
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None
    
def calculate_cosine_similarity(vector1, vector2):
    """
    Calculates the cosine similarity between two vectors.
    """
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)
    return dot_product / (magnitude1 * magnitude2)
