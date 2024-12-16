import logging
import json
import os
from io import BytesIO

import requests
from PIL import Image
import spacy
from django.db.models import F, Q
from asgiref.sync import sync_to_async
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.response import JsonResponse

from .models import PlantData as DjangoPlantData, QAEntry
from .pydanticai import PlantData, Agent, InferenceResult
from .utils import calculate_cosine_similarity, get_embedding

logger = logging.getLogger(__name__)
agent = Agent()
nlp = spacy.load("en_core_web_sm")


def find_closest_match_nlp(text, options):
    """
    Finds the closest matching string from a list of options using spaCy's similarity.
    """
    doc1 = nlp(text)
    max_similarity = 0
    closest_match = None
    for option in options:
        doc2 = nlp(option)
        similarity = doc1.similarity(doc2)
        if similarity > max_similarity:
            max_similarity = similarity
            closest_match = option
    return closest_match


async def get_similar_qa_entry(question_vector, plant, threshold=0.75):
    """
    Retrieves a similar Q&A entry from the database based on cosine similarity.
    """
    qa_entries = await QAEntry.objects.filter(plant=plant).aall()
    for entry in qa_entries:
        similarity = calculate_cosine_similarity(question_vector, entry.question_vector)
        if similarity >= threshold:
            return entry
    return None


@sync_to_async
def create_qa_entry(plant, question_text, question_vector, answer_text):
    """
    Creates a new Q&A entry in the database.
    """
    QAEntry.objects.create(
        plant=plant,
        question_text=question_text,
        question_vector=question_vector,
        answer_text=answer_text
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_image(request):
    if request.method == 'POST':
        try:
            # --- Validation ---
            if 'image' not in request.FILES:
                raise ValueError("No image provided")
            if 'plant_id' not in request.POST:
                raise ValueError("No plant_id provided")

            image_file = request.FILES['image']
            plant_id = request.POST.get('plant_id')

            # --- Retrieve Plant Data ---
            try:
                plant = await DjangoPlantData.objects.aget(id=plant_id)
            except DjangoPlantData.DoesNotExist:
                raise ValueError("Plant not found")

            plant.image = image_file
            await sync_to_async(plant.save)()

            # --- Preprocess Image ---
            image = Image.open(image_file)
            image = image.resize((224, 224))
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            # --- Send to OpenAI API ---
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not found.")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}"
            }
            payload = {
                "model": "image-classification-model",  # Replace with your model name
                "image": image_bytes.read().decode('latin-1')  # Encode image bytes appropriately
            }

            response = requests.post("https://api.openai.com/v1/images/classifications", headers=headers, json=payload)
            response.raise_for_status()

            # --- Parse Prediction Results ---
            prediction_results = response.json()
            # ... (Extract relevant prediction information) ...

            return JsonResponse({'status': 'success', 'prediction': prediction_results})

        except ValueError as ve:
            logger.error(f"ValueError in upload_image: {ve}")
            return JsonResponse({'error': str(ve)}, status=400)
        except requests.exceptions.RequestException as re:
            logger.error(f"RequestException in upload_image: {re}")
            return JsonResponse({'error': 'Failed to get a prediction from the model'}, status=500)
        except Exception as e:
            logger.exception(f"An unexpected error occurred in upload_image: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def ask_botanical_question(request):
    """
    This endpoint allows authenticated users to ask questions about plants.
    """
    try:
        user_query = request.data.get('query', '')
        plant_name = request.data.get('plant_name', '')
        similarity_threshold = float(os.environ.get("SIMILARITY_THRESHOLD", 0.75))

        # --- Validation ---
        if not user_query:
            raise ValueError("Missing 'query' parameter.")
        if not plant_name:
            raise ValueError("Missing 'plant_name' parameter.")

        # --- Find the Plant ---
        query = Q(common_name__iexact=plant_name) | Q(scientific_name__iexact=plant_name)
        django_plant = await DjangoPlantData.objects.filter(query).afirst()
        if django_plant is None:
            plant_names = [plant.common_name for plant in await DjangoPlantData.objects.aall()]
            closest_match = find_closest_match_nlp(plant_name, plant_names)
            if closest_match:
                django_plant = await DjangoPlantData.objects.aget(common_name=closest_match)
            else:
                raise ValueError(f"Plant '{plant_name}' not found.")

        # --- Enhanced NLP ---
        doc = nlp(user_query)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        logger.info(f"Entities identified: {entities}")

        # --- Diagnostic Question ---
        if any(label in ["PEST", "DISEASE", "SYMPTOM"] for _, label in entities):
            prediction_results = request.data.get('prediction')
            if not prediction_results:
                raise ValueError("Missing 'prediction' data for diagnostic question.")

            diagnosis = refine_diagnosis(
                prediction_results,
                django_plant.common_name,
                django_plant.common_diseases,
                django_plant.common_pests,
                user_query
            )

            response_data = {
                'answer': f"{diagnosis}",
                'common_diseases': django_plant.common_diseases,
                'common_pests': django_plant.common_pests,
            }
            return Response(response_data)

        # --- General Question ---
        question_embedding = get_embedding(user_query)
        if question_embedding is None:
            raise ValueError("Failed to generate user query embedding.")

        similar_qa_entry = await get_similar_qa_entry(question_embedding, django_plant, similarity_threshold)
        if similar_qa_entry:
            logger.info("Found similar Q&A entry in the database.")
            return Response({'answer': similar_qa_entry.answer_text})

        plant_data = PlantData(
            common_name=django_plant.common_name,
            scientific_name=django_plant.scientific_name,
            # ... other relevant fields from django_plant ...
        )
        inference_result = agent.run_inference(plant_data, user_query)
        if isinstance(inference_result, InferenceResult):
            answer = inference_result.answer
            await create_qa_entry(
                plant=django_plant,
                question_text=user_query,
                question_vector=question_embedding,
                answer_text=answer
            )
            return Response({'answer': answer})
        else:
            raise ValueError("Failed to generate an answer.")

    except ValueError as ve:
        logger.error(f"ValueError in ask_botanical_question: {ve}")
        return Response({'error': str(ve)}, status=400)
    except Exception as e:
        logger.exception(f"An unexpected error occurred in ask_botanical_question: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=500)


def refine_diagnosis(prediction, plant_name, common_diseases, common_pests, user_query):
    """
    Refines the initial prediction by combining it with other information.
    """
    refined_diagnosis = f"Based on the image analysis and your query, "

    if prediction['disease_probability'] > 0.8:
        predicted_disease = prediction['disease_label']
        if predicted_disease in common_diseases:
            refined_diagnosis += f"it seems like your {plant_name} might have {predicted_disease}. "
        else:
            refined_diagnosis += f"it seems like your {plant_name} might have a disease similar to {predicted_disease}. "
    else:
        refined_diagnosis += f"I couldn't confidently identify a specific disease on your {plant_name}. "

    if prediction.get('pest_probability', 0) > 0.8:
        predicted_pest = prediction['pest_label']
        if predicted_pest in common_pests:
            refined_diagnosis += f"I also noticed signs of {predicted_pest}. "
        else:
            refined_diagnosis += f"I also noticed signs of a pest similar to {predicted_pest}. "

    doc = nlp(user_query)
    symptom_keywords = [ent.text for ent in doc.ents if ent.label_ == "SYMPTOM"]
    if symptom_keywords:
        refined_diagnosis += f"You mentioned symptoms like {', '.join(symptom_keywords)}. "

    if prediction['disease_probability'] < 0.8 and prediction.get('pest_probability', 0) < 0.8:
        refined_diagnosis += "To help me diagnose the issue more accurately, " \
                             "could you please provide more details about the symptoms " \
                             "or any recent changes in the plant's environment?"

    return refined_diagnosis