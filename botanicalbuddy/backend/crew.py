# backend/crew.py
import html
import logging
import os
import subprocess
import tempfile
from enum import Enum
from typing import List, Optional

import joblib
import requests
import spacy
from crewai import Agent, Crew, Process, Task
from crewai.llm import BaseLLM  # Import BaseLLM instead of Gemini
from crewai_tools import BaseTool  # Import BaseTool
from crewai_tools import WebSearchTools
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, ValidationError, validator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global Constants ---
DEFAULT_MAX_ITERATIONS = 10
SANDBOX_TIMEOUT = 10  # seconds
TREFLE_API_BASE_URL = "https://trefle.io/api/v1"

# --- Load SpaCy Model ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("Downloading spaCy model 'en_core_web_sm'...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Load or Train scikit-learn Intent Classifier ---
try:
    intent_classifier = joblib.load("intent_classifier.joblib")
    tfidf_vectorizer = joblib.load("tfidf_vectorizer.joblib")
    logging.info("Loaded pre-trained intent classifier.")
except FileNotFoundError:
    logging.warning("Pre-trained intent classifier not found. Please train and save one for production.")
    # Example training data - replace with your actual dataset
    training_data = [
        ("How do I water my roses?", "PLANT_CARE"),
        ("What kind of plant is this?", "IDENTIFY_PLANT"),
        ("Tell me about soil for basil.", "SOIL_INFO"),
        ("Origin of the Venus flytrap?", "BOTANICAL_INFO"),
        ("General question about growing herbs.", "GENERAL_QUERY"),
    ]
    train_texts = [text for text, _ in training_data]
    train_labels = [label for _, label in training_data]

    tfidf_vectorizer = TfidfVectorizer()
    train_features = tfidf_vectorizer.fit_transform(train_texts)

    intent_classifier = LogisticRegression()
    intent_classifier.fit(train_features, train_labels)

    joblib.dump(intent_classifier, "intent_classifier.joblib")
    joblib.dump(tfidf_vectorizer, "tfidf_vectorizer.joblib")
    logging.info("Trained and saved basic intent classifier.")

# --- Validation Schemas ---
class PlantInfoRequest(BaseModel):
    plant_name: str

    @validator("plant_name")
    def validate_plant_name(cls, value):
        if not value.strip():
            raise ValueError("Plant name cannot be empty.")
        if len(value) < 2:
            raise ValueError("Plant name must be at least 2 characters long.")
        return value.strip()

# --- Tool Definitions with Enhanced Security and Error Handling ---
class GetPlantInfoTool(BaseTool):
    name: str = "get_plant_info"
    description: str = "Securely retrieves detailed information about a plant by its name using a local knowledge base."

    def _run(self, plant_name: str) -> str:
        try:
            PlantInfoRequest(plant_name=plant_name)
            sanitized_plant_name = html.escape(plant_name)
            logging.info(f"GetPlantInfoTool: Retrieving info for '{sanitized_plant_name}'")

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=True) as tmp_file:
                tmp_file.write(f"""
def get_plant_details(name):
    known_plants = {{"rose": "Roses are beautiful.", "tulip": "Tulips bloom in spring."}}
    return known_plants.get(name.lower(), "Plant information not found in local database.")

if __name__ == "__main__":
    plant_name = "{sanitized_plant_name}"
    result = get_plant_details(plant_name)
    print(result)
""")
                tmp_file.flush()

                try:
                    process = subprocess.run(
                        ["python", tmp_file.name],
                        capture_output=True,
                        text=True,
                        timeout=SANDBOX_TIMEOUT,
                    )
                    if process.returncode == 0:
                        return process.stdout.strip()
                    else:
                        logging.error(f"GetPlantInfoTool: Sandbox failed (code {process.returncode}): {process.stderr}")
                        return f"Error retrieving information for '{sanitized_plant_name}' from local source."
                except subprocess.TimeoutExpired:
                    logging.error(f"GetPlantInfoTool: Sandbox timed out for '{sanitized_plant_name}'.")
                    return f"Retrieval of information for '{sanitized_plant_name}' from local source timed out."
                except Exception as e:
                    logging.error(f"GetPlantInfoTool: Sandbox error for '{sanitized_plant_name}': {e}")
                    return f"Error retrieving information for '{sanitized_plant_name}' from local source."

        except ValidationError as e:
            logging.warning(f"GetPlantInfoTool: Invalid plant name: {e}")
            return f"Invalid plant name provided: {e}"
        except Exception as e:
            logging.error(f"GetPlantInfoTool: Unexpected error: {e}")
            return f"An unexpected error occurred while retrieving information for '{plant_name}' from local source."

class DuckDuckGoTool(BaseTool):
    name: str = "search_internet"
    description: str = "Securely searches the internet for information."
    search_tool: DuckDuckGoSearchRun = DuckDuckGoSearchRun()

    def _run(self, query: str) -> str:
        sanitized_query = html.escape(query)
        logging.info(f"DuckDuckGoTool: Searching for '{sanitized_query}'")
        try:
            return self.search_tool.run(sanitized_query)
        except Exception as e:
            logging.error(f"DuckDuckGoTool: Search error for '{sanitized_query}': {e}")
            return f"Error during internet search for '{sanitized_query}'."

class TrefleTool(BaseTool):
    name: str = "get_trefle_info"
    description: str = "Securely retrieves detailed information about a plant from the Trefle database."

    def _run(self, plant_name: str) -> str:
        TREFLE_API_TOKEN = os.getenv("TREFLE_API_TOKEN")
        if not TREFLE_API_TOKEN:
            logging.error("Trefle API token not found in environment variables.")
            return "Error: Trefle API token not configured."

        try:
            PlantInfoRequest(plant_name=plant_name)
            sanitized_plant_name = html.escape(plant_name)
            logging.info(f"TrefleTool: Retrieving info for '{sanitized_plant_name}' from Trefle.")

            search_url = f"{TREFLE_API_BASE_URL}/plants/search"
            params = {"token": TREFLE_API_TOKEN, "q": sanitized_plant_name}
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            search_data = response.json()['data']

            if not search_data:
                return f"No plant found on Trefle matching '{sanitized_plant_name}'."

            plant_id = search_data[0]['id']
            plant_url = f"{TREFLE_API_BASE_URL}/plants/{plant_id}"
            plant_response = requests.get(plant_url, params={"token": TREFLE_API_TOKEN})
            plant_response.raise_for_status()
            plant_data = plant_response.json()['data']

            common_name = plant_data.get('common_name')
            scientific_name = plant_data.get('scientific_name')
            family_name = plant_data.get('family_common_name')
            genus = plant_data.get('genus')
            native_status = plant_data.get('native_status')
            year = plant_data.get('year')

            return f"Trefle Info for {common_name or scientific_name}:\n" \
                   f"Scientific Name: {scientific_name or 'N/A'}\n" \
                   f"Family: {family_name or 'N/A'}\n" \
                   f"Genus: {genus or 'N/A'}\n" \
                   f"Native Status: {native_status or 'N/A'}\n" \
                   f"Year Discovered: {year or 'N/A'}"

        except ValidationError as e:
            logging.warning(f"TrefleTool: Invalid plant name: {e}")
            return f"Invalid plant name provided: {e}"
        except requests.exceptions.RequestException as e:
            logging.error(f"TrefleTool: API request error: {e}")
            return f"Error communicating with the Trefle database for '{plant_name}'."
        except Exception as e:
            logging.error(f"TrefleTool: Unexpected error: {e}")
            return f"An unexpected error occurred while retrieving information for '{plant_name}' from Trefle."

# --- Agent Definitions with Explicit LLM and Trefle Tool ---
# You'll need to initialize your custom LLM here
from backend.utils.GeminiLLM import GeminiLLM
gemini_llm = GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))

plant_identifier = Agent(
    role="Expert Plant Identifier",
    goal="Accurately and securely identify plant species from user input using both local knowledge and the Trefle database.",
    backstory="A highly trained botanical expert with access to a comprehensive plant database.",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm,  # Use your custom Gemini LLM
    tools=[GetPlantInfoTool(), TrefleTool()],
)

customer_service_expert = Agent(
    role="Tier 1 Customer Support Specialist",
    goal="Provide initial, helpful, and safe assistance to plant-related queries.",
    backstory="A friendly and knowledgeable support professional focused on secure interactions.",
    verbose=True,
    allow_delegation=True,
    llm=gemini_llm,  # Use your custom Gemini LLM
    tools=[DuckDuckGoTool()],
)

soil_scientist = Agent(
    role="Certified Soil Analysis Expert",
    goal="Analyze soil-related queries and provide safe, evidence-based recommendations.",
    backstory="A meticulous soil scientist dedicated to accurate and safe advice.",
    verbose=True,
    allow_delegation=False,
    llm=gemini_llm,  # Use your custom Gemini LLM
    tools=[DuckDuckGoTool()],
)

botanist = Agent(
    role="Doctor of Botany",
    goal="Provide comprehensive and accurate information on plant biology and origins, leveraging the Trefle database.",
    backstory="A seasoned botanist with a deep understanding of plant science and access to extensive databases.",
    verbose=True,
    allow_delegation=True,
    llm=gemini_llm,  # Use your custom Gemini LLM
    tools=[DuckDuckGoTool(), TrefleTool()],
)

horticulturalist = Agent(
    role="Master Horticulturalist",
    goal="Offer practical, safe, and effective advice on plant care and cultivation.",
    backstory="An experienced horticulturalist with a strong emphasis on safety and best practices.",
    verbose=True,
    llm=gemini_llm,  # Use your custom Gemini LLM
    tools=[DuckDuckGoTool()],
)

# --- Intent Recognition using scikit-learn ---
class Intent(Enum):
    IDENTIFY_PLANT = "IDENTIFY_PLANT"
    PLANT_CARE = "PLANT_CARE"
    SOIL_INFO = "SOIL_INFO"
    BOTANICAL_INFO = "BOTANICAL_INFO"
    GENERAL_QUERY = "GENERAL_QUERY"

def dynamically_assign_tasks(user_query: str, plant_data: Optional[dict] = None) -> List[Task]:
    tasks = []
    sanitized_query = html.escape(user_query)
    logging.info(f"Dynamically assigning tasks for query: '{sanitized_query}'")

    try:
        query_features = tfidf_vectorizer.transform([user_query])
        predicted_intent = intent_classifier.predict(query_features)[0]
        logging.info(f"Predicted intent: {predicted_intent}")

        if predicted_intent == Intent.IDENTIFY_PLANT.value:
            tasks.append(Task(
                description=f"Identify the plant: '{sanitized_query}'. Provide common and scientific names, using both local knowledge and the Trefle database.",
                expected_output="The common and scientific name of the plant, with additional details from Trefle if available.",
                agent=plant_identifier
            ))
        elif predicted_intent == Intent.PLANT_CARE.value:
            tasks.append(Task(
                description=f"Provide safe care instructions for: '{sanitized_query}'. Include watering, sunlight, soil, and specific needs.",
                expected_output="Comprehensive and safe care instructions.",
                agent=horticulturalist
            ))
        elif predicted_intent == Intent.SOIL_INFO.value:
            tasks.append(Task(
                description=f"Analyze the soil-related query: '{sanitized_query}'. Provide safe recommendations.",
                expected_output="Safe advice on soil composition, amendments, or fertilization.",
                agent=soil_scientist
            ))
        elif predicted_intent == Intent.BOTANICAL_INFO.value:
            tasks.append(Task(
                description=f"Research botanical aspects of: '{sanitized_query}'. Include origin, taxonomy, and safe handling, using the Trefle database.",
                expected_output="Information on origin, taxonomy, and safe handling, with details from Trefle.",
                agent=botanist
            ))
        elif predicted_intent == Intent.GENERAL_QUERY.value:
            tasks.append(Task(
                description=f"Handle the general plant query: '{sanitized_query}'. Provide info or route securely.",
                expected_output="A safe and helpful response or secure routing.",
                agent=customer_service_expert
            ))
        else:
            logging.warning(f"No specific intent recognized for query: '{sanitized_query}'.")
            tasks.append(Task(
                description=f"Handle the general plant query: '{sanitized_query}'. Provide info or route securely.",
                expected_output="A safe and helpful response or secure routing.",
                agent=customer_service_expert
            ))

        for task in tasks:
            if not isinstance(task, Task):
                logging.error(f"Error: Non-Task object found in tasks: {task}")
                raise ValueError("Error in task assignment.")

        logging.info(f"Successfully assigned {len(tasks)} tasks.")
        return tasks

    except Exception as e:
        logging.error(f"Error dynamically assigning tasks: {e}")
        return [Task(description="Error processing your request.", expected_output="An error message.", agent=customer_service_expert)]

# --- Crew Creation with Error Handling ---
def create_crew_with_dynamic_tasks(user_query: str) -> Crew:
    try:
        tasks = dynamically_assign_tasks(user_query)
        crew = Crew(
            agents=[plant_identifier, customer_service_expert, soil_scientist, botanist, horticulturalist],
            tasks=tasks,
            verbose=True,
            process=Process.sequential,
            max_rpm=30,
            max_iterations=DEFAULT_MAX_ITERATIONS
        )
        logging.info("Successfully created crew with dynamic tasks.")
        return crew
    except ValidationError as ve:
        logging.error(f"Pydantic validation error during crew creation: {ve}")
        raise
    except Exception as e:
        logging.error(f"Error creating crew with dynamic tasks: {e}")
        raise