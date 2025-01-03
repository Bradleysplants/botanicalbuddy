# backend/pydanticai.py
from typing import List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, field_validator
import openai
import os
import logging
import httpx

logger = logging.getLogger(__name__)

class VectorData(BaseModel):
    data: List[float]

    @field_validator("data")
    def check_data_length(cls, value):
        if not value:
            raise ValueError("Vector data cannot be empty.")
        return value

class PlantData(BaseModel):
    plant_name: str
    scientific_name: str = None
    description: str = None
    care_instructions: str = None
    soil_type: str = None
    water_requirements: str = None
    sunlight_requirements: str = None
    vector_data: List[float] = None
    similarity: Optional[float] = None

    @field_validator('plant_name')
    def check_required_fields(cls, v):
        if v is None:
            raise ValueError(f"Field 'plant_name' is required.")
        return v

class InferenceResult(BaseModel):
    answer: str
    system_message: str = ""
    temperature: int = 0
    top_k: int = 0

@runtime_checkable
class AIAgent(Protocol):
    async def run_inference(self, plant_data: PlantData, user_query: str) -> InferenceResult:
        ...

class OpenAIAgent:
    # ... (Your existing OpenAIAgent class remains the same)
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found.")

        self.model_name = os.environ.get("OPENAI_MODEL_NAME", "text-davinci-003")
        self.system_message = os.environ.get("OPENAI_SYSTEM_MESSAGE", "You are a helpful botanical assistant.")
        openai.api_key = self.openai_api_key

    async def run_inference(self, plant_data: PlantData, user_query: str) -> InferenceResult:
        try:
            prompt = f"""
            You are a helpful botanical assistant. Respond to the user's query about the following plant:

            Plant Name: {plant_data.plant_name or "N/A"}
            Scientific Name: {plant_data.scientific_name or "N/A"}
            Description: {plant_data.description or "N/A"}
            Care Instructions: {plant_data.care_instructions or "N/A"}
            Soil Type: {plant_data.soil_type or "N/A"}
            Water Requirements: {plant_data.water_requirements or "N/A"}
            Sunlight Requirements: {plant_data.sunlight_requirements or "N/A"}

            User Query: {user_query}
            """

            response = await openai.Completion.acreate(
                model=self.model_name,
                prompt=prompt,
                max_tokens=250,
            )
            inference = response.choices[0].text.strip()
            return InferenceResult(answer=inference, system_message=self.system_message)

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return InferenceResult(answer=f"An OpenAI API error occurred: {e}", system_message=self.system_message)
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {e}")
            return InferenceResult(answer="OpenAI API rate limit exceeded.", system_message=self.system_message)
        except openai.InvalidRequestError as e:
            logger.error(f"Invalid OpenAI API request: {e}")
            return InferenceResult(answer="Invalid OpenAI API request.", system_message=self.system_message)
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}") # Log full traceback
            return InferenceResult(answer=f"An unexpected error occurred: {e}", system_message=self.system_message)

class OllamaAgent:
    def __init__(self):
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm_model_name = os.environ.get("OLLAMA_LLM_MODEL_NAME", "llama2")  # For LLM
        self.embedding_model_name = os.environ.get("OLLAMA_EMBEDDING_MODEL_NAME", "all-mpnet-base-v2") # For embeddings

    async def get_embeddings(self, text: str) -> List[float]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={"model": self.embedding_model_name, "prompt": text}
                )
                response.raise_for_status()
                return response.json().get("embedding")
        except httpx.RequestError as e:
            logger.error(f"Error communicating with Ollama for embeddings: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API (embeddings) error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error during Ollama embedding generation: {e}")
            return None

    async def run_inference(self, plant_data: PlantData, user_query: str) -> InferenceResult:
        try:
            # 1. Generate embeddings for the plant data
            plant_info = f"""
                Plant Name: {plant_data.plant_name or "N/A"}
                Scientific Name: {plant_data.scientific_name or "N/A"}
                Description: {plant_data.description or "N/A"}
                Care Instructions: {plant_data.care_instructions or "N/A"}
                Soil Type: {plant_data.soil_type or "N/A"}
                Water Requirements: {plant_data.water_requirements or "N/A"}
                Sunlight Requirements: {plant_data.sunlight_requirements or "N/A"}
            """
            plant_embedding = await self.get_embeddings(plant_info)
            if not plant_embedding:
                return InferenceResult(answer="Could not generate embeddings for plant data.", system_message=f"Ollama Error - {self.embedding_model_name}")

            # 2. Generate embeddings for the user query
            query_embedding = await self.get_embeddings(user_query)
            if not query_embedding:
                return InferenceResult(answer="Could not generate embeddings for the user query.", system_message=f"Ollama Error - {self.embedding_model_name}")

            # **(Here you would typically perform similarity search/retrieval using plant_embedding and query_embedding)**
            # For simplicity in this example, we'll just include the plant info in the prompt.
            # In a real application, you'd use the embeddings to find relevant information.

            # 3. Run inference with the LLM
            prompt = f"""
            You are a helpful botanical assistant. Respond to the user's query, using the following information about the plant:

            {plant_info}

            User Query: {user_query}
            """

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "prompt": prompt,
                        "model": self.llm_model_name,
                        "stream": False
                    }
                )
                response.raise_for_status()
                response_data = response.json()
                completion_text = response_data.get("response", "No response from Ollama.")
                return InferenceResult(answer=completion_text, system_message=f"Ollama - {self.llm_model_name}")

        except httpx.RequestError as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return InferenceResult(answer=f"Could not connect to Ollama: {e}", system_message=f"Ollama Error - {self.llm_model_name}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            return InferenceResult(answer=f"Ollama API error: {e.response.status_code}", system_message=f"Ollama Error - {self.llm_model_name}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred during Ollama inference: {e}")
            return InferenceResult(answer=f"An unexpected error occurred with Ollama: {e}", system_message=f"Ollama Error - {self.llm_model_name}")

# --- Agent Factory ---
def create_agent() -> AIAgent:
    agent_type = os.environ.get("AI_AGENT_TYPE", "openai").lower()
    if agent_type == "openai":
        return OpenAIAgent()
    elif agent_type == "local":
        return OllamaAgent()
    else:
        raise ValueError(f"Unknown AI_AGENT_TYPE: {agent_type}. Choose 'openai' or 'local'.")