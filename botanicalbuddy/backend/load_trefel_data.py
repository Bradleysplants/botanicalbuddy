import os
import django
import requests
import json
import logging
from tqdm import tqdm
from typing import List, Dict, Any

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'botanicalbuddy.settings')
django.setup()

from backend.models import PlantData
from backend.utils import get_embedding  # Import from backend.utils

logger = logging.getLogger(__name__)

TREFLE_API_KEY = os.environ.get("TREFLE_API_KEY")
if not TREFLE_API_KEY:
    raise ValueError("TREFLE_API_KEY environment variable not found.")

BASE_URL = "https://trefle.io/api/v1/plants"


def fetch_plant_data(page: int = 1) -> List[Dict[str, Any]]:
    """Fetches plant data from the Trefle API."""
    url = f"{BASE_URL}?token={TREFLE_API_KEY}&page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()['data']
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Trefle API: {e}")
        return []


def fetch_plant_details(plant_id: int) -> Dict[str, Any]:
    """Fetches detailed information for a specific plant from Trefle."""
    url = f"{BASE_URL}/{plant_id}?token={TREFLE_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching plant details for ID {plant_id}: {e}")
        return {}


def save_plant_to_db(plant_data: Dict[str, Any]):
    """Saves plant data to the database, including generating and storing embeddings."""
    try:
        details = fetch_plant_details(plant_data.get('id'))
        if not details:
            return

        description = details.get("specifications", {}).get("description")
        if description:
            try:
                vector_data = get_embedding(description)
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for plant {details.get('common_name')}: {e}"
                )
                vector_data = None
        else:
            vector_data = None

        PlantData.objects.update_or_create(
            trefle_id=details.get('id'),
            defaults={
                'common_name': details.get('common_name'),
                'scientific_name': details.get('scientific_name'),
                'slug': details.get('slug'),
                'image_url': details.get("image_url"),
                'year': details.get("year"),
                'family_common_name': details.get("family_common_name"),
                'family': details.get("family"),
                'genus': details.get("genus"),
                'growth_habit': details.get("growth_habit"),
                'maximum_height': details.get("maximum_height", {}).get("cm"),
                'flower_color': details.get("flower_color"),
                'native_to': details.get("native_to"),
                'description': description,
                'care_instructions': details.get("care_instructions"),
                'soil_type': details.get("soil_type"),
                'water_requirements': details.get("water_requirements"),
                'sunlight_requirements': details.get("sunlight_requirements"),
                'vector_data': vector_data
            })
    except Exception as e:
        logger.error(f"Error saving plant to database: {e}")


def main():
    """Main function to fetch and save plant data."""
    page = 1
    total_plants = 0
    while True:
        plants = fetch_plant_data(page)
        if not plants:
            break

        total_plants += len(plants)
        print(f"Fetching page {page}: {len(plants)} plants")
        for plant in tqdm(plants, desc=f"Saving plants from page {page}"):
            save_plant_to_db(plant)
        page += 1

    print(f"Finished loading plant data. Total Plants loaded: {total_plants}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()