from typing import List, Optional
from pydantic import BaseModel, field_validator
import openai
import os
import logging

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
    inference: str
    system_message: str = ""
    temperature: int = 0
    top_k: int = 0

class Agent:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found.")

        self.system_message = os.environ.get("OPENAI_SYSTEM_MESSAGE", "You are a helpful botanical assistant.")
        openai.api_key = self.openai_api_key

    async def run_sync(self, query_vector: VectorData, plant_data: List[PlantData], user_query: str = "") -> InferenceResult:
        try:
            most_similar_plant = max(plant_data, key=lambda p: p.similarity) if plant_data else None

            if most_similar_plant:
                plant = most_similar_plant
                query_lower = user_query.lower()
                if "care" in query_lower:
                    instructions = "Provide detailed care instructions for this plant, including watering, sunlight, soil, and fertilization recommendations. Format your response as a bulleted list."
                elif "pest" in query_lower:
                    instructions = "Identify potential pests that might affect this plant and suggest effective methods for pest control. Format your response as a numbered list."
                elif "light" in query_lower:
                    instructions = "Describe the ideal lighting conditions for this plant (e.g., full sun, partial shade, indirect light)."
                else:
                    instructions = "Provide general information about this plant."

                prompt = f"""
                Plant Information:
                - Common Name: {plant.plant_name or "N/A"}
                - Scientific Name: {plant.scientific_name or "N/A"}
                - Description: {plant.description or "N/A"}
                - Care Instructions: {plant.care_instructions or "N/A"}
                - Soil Type: {plant.soil_type or "N/A"}
                - Water Requirements: {plant.water_requirements or "N/A"}
                - Sunlight Requirements: {plant.sunlight_requirements or "N/A"}

                User Query: {user_query}

                {instructions}
                """

                response = await openai.Completion.acreate(
                    model="text-davinci-003",  # Or your preferred model
                    prompt=prompt,
                    max_tokens=250,
                )
                inference = response.choices[0].text.strip()
            else:
                inference = "No similar plants found."

            return InferenceResult(inference=inference, system_message=self.system_message)

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return InferenceResult(inference=f"An OpenAI API error occurred: {e}", system_message=self.system_message)
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {e}")
            return InferenceResult(inference="OpenAI API rate limit exceeded.", system_message=self.system_message)
        except openai.InvalidRequestError as e:
            logger.error(f"Invalid OpenAI API request: {e}")
            return InferenceResult(inference="Invalid OpenAI API request.", system_message=self.system_message)
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}") # Log full traceback
            return InferenceResult(inference=f"An unexpected error occurred: {e}", system_message=self.system_message)