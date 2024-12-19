# backend/views.py
import logging
import json
import os
from io import BytesIO

import requests  # For making API requests to your model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from django.db.models import F, Q
import spacy
import numpy as np
from .serializers import PlantDataSerializer  # Import your serializer
from .serializers import QAEntrySerializer

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
        similarity = calculate_cosine_similarity(question_vector,
                                                entry.question_vector)
        if similarity >= threshold:
            return entry
    return None


@sync_to_async
def create_qa_entry(plant, question_text, question_vector, answer_text):
    """
    Creates a new Q&A entry in the database.
    """
    QAEntry.objects.create(plant=plant,
                           question_text=question_text,
                           question_vector=question_vector,
                           answer_text=answer_text)

@api_view(['GET'])
@permission_classes([AllowAny])
def session_view(request):
    # Access session data
    username = request.session.get('username')

    # Return session data or an appropriate response
    if username:
        return Response({'username': username})
    else:
        return Response({'message': 'No session data found'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_image(request):
    if request.method == 'POST':
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)

        image_file = request.FILES['image']
        plant_id = request.POST.get('plant_id')

        try:
            plant = await DjangoPlantData.objects.aget(id=plant_id)
            plant.image = image_file
            await sync_to_async(plant.save)()

            # Preprocess the image using Pillow (PIL)
            image = image.open(image_file)
            image = image.resize(
                (224, 224))  # Example resize, adjust as needed
            # ... other preprocessing steps (e.g., normalization) ...

            # Prepare the image for sending to the OpenAI API
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG')  # Or appropriate format
            image_bytes.seek(0)

            # Make a request to your OpenAI model API
            model_api_url = "your_openai_model_api_endpoint"  # Replace with your actual endpoint
            response = requests.post(model_api_url,
                                     files={'image': image_bytes})
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the prediction results
            prediction_results = response.json()
            # ... extract the relevant prediction information (e.g., disease label, probability) ...

            return JsonResponse(
                {'status': 'success',
                 'prediction': prediction_results})

        except DjangoPlantData.DoesNotExist:
            return JsonResponse({'error': 'Plant not found'}, status=404)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with the model API: {e}")
            return JsonResponse({
                'error': 'Failed to get a prediction from the model'
            },
                status=500)
        except Exception as e:
            logger.exception(f"An unexpected error occurred in upload_image: {e}")
            return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qa_entry(request, pk):
    try:
        qa_entry = QAEntry.objects.get(pk=pk)
    except QAEntry.DoesNotExist:
        return Response({'error': 'QA Entry not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = QAEntrySerializer(qa_entry)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def ask_botanical_question(request):
    """
    This endpoint allows authenticated users to ask questions about plants.
    """
    try:
        user_query = request.data.get('query', '')
        plant_name = request.data.get('plant_name', '')
        similarity_threshold = float(
            os.environ.get("SIMILARITY_THRESHOLD", 0.75))

        if not user_query:
            logger.warning("Missing 'query' parameter.")
            return Response({'error': 'Missing query parameter.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not plant_name:
            logger.warning("Missing 'plant_name' parameter.")
            return Response({'error': 'Missing plant_name parameter.'},
                            status=status.HTTP_400_BAD_REQUEST)

        query = Q(common_name__iexact=plant_name) | Q(
            scientific_name__iexact=plant_name)
        django_plant = await DjangoPlantData.objects.filter(query).afirst()
        if django_plant is None:
            plant_names = [
                plant.common_name
                for plant in await DjangoPlantData.objects.aall()
            ]
            closest_match = find_closest_match_nlp(plant_name, plant_names)
            if closest_match:
                django_plant = await DjangoPlantData.objects.aget(
                    common_name=closest_match)
            else:
                logger.warning(f"Plant '{plant_name}' not found.")
                return Response({'error': f"Plant '{plant_name}' not found."},
                                status=status.HTTP_404_NOT_FOUND)

        # --- Enhanced NLP ---
        doc = nlp(user_query)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        logger.info(f"Entities identified: {entities}")

        # Example: Check if the query is about pests or diseases
        if any(label in ["PEST", "DISEASE", "SYMPTOM"]
               for _, label in entities):
            # Assuming you have the prediction results from the upload_image view
            prediction_results = request.data.get('prediction')

            # Combine prediction with other information
            diagnosis = refine_diagnosis(prediction_results,
                                        django_plant.common_name,
                                        django_plant.common_diseases,
                                        django_plant.common_pests, user_query)

            # Use the refined diagnosis in the response
            response_data = {
                'answer': f"{diagnosis}"
            }  # Include the diagnosis in the answer

            # Add information about common diseases and pests for the plant
            response_data['common_diseases'] = django_plant.common_diseases
            response_data['common_pests'] = django_plant.common_pests

            return Response(response_data)

        question_embedding = get_embedding(user_query)
        if question_embedding is None:
            logger.error("Failed to generate user query embedding.")
            return Response({
                'error': 'Failed to generate user query embedding.'
            },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check for similar Q&A entries
        similar_qa_entry = await get_similar_qa_entry(
            question_embedding, django_plant, similarity_threshold)
        if similar_qa_entry:
            logger.info("Found similar Q&A entry in the database.")
            return Response({'answer': similar_qa_entry.answer_text})

        # If no similar entry is found, generate a new answer
        plant_data = PlantData(
            common_name=django_plant.common_name,
            scientific_name=django_plant.scientific_name,
            # ... other relevant fields from django_plant ...
        )
        inference_result = agent.run_inference(plant_data, user_query)
        if isinstance(inference_result, InferenceResult):
            answer = inference_result.answer
            # Create a new Q&A entry asynchronously
            await create_qa_entry(plant=django_plant,
                                   question_text=user_query,
                                   question_vector=question_embedding,
                                   answer_text=answer)
            return Response({'answer': answer})
        else:
            logger.error(f"Inference failed: {inference_result}")
            return Response({'error': 'Failed to generate an answer.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON data received: {request.body}")
        return Response({'error': 'Invalid JSON data in request body.'},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return Response({'error': 'An unexpected error occurred.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plant_data(request, pk):
    try:
        plant = PlantData.objects.get(pk=pk)
    except PlantData.DoesNotExist:
        return Response({'error': 'Plant not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PlantDataSerializer(plant)
    return Response(serializer.data)


def refine_diagnosis(prediction, plant_name, common_diseases, common_pests,
                    user_query):
    """
    Refines the initial prediction by combining it with other information.
    """
    refined_diagnosis = f"Based on the image analysis and your query, "

    # --- Disease Diagnosis ---
    if prediction['disease_probability'] > 0.8:  # Example threshold
        predicted_disease = prediction['disease_label']
        if predicted_disease in common_diseases:
            refined_diagnosis += f"it seems like your {plant_name} might have {predicted_disease}. "
        else:
            refined_diagnosis += f"it seems like your {plant_name} might have a disease similar to {predicted_disease}. "
    else:
        refined_diagnosis += f"I couldn't confidently identify a specific disease on your {plant_name}. "

    # --- Pest Diagnosis ---
    # (Assuming your model also predicts pests with a 'pest_probability' and 'pest_label')
    if prediction['pest_probability'] > 0.8:
        predicted_pest = prediction['pest_label']
        if predicted_pest in common_pests:
            refined_diagnosis += f"I also noticed signs of {predicted_pest}. "
        else:
            refined_diagnosis += f"I also noticed signs of a pest similar to {predicted_pest}. "

    # --- Symptom Analysis ---
    # Use spaCy to extract symptom keywords from the user query
    doc = nlp(user_query)
    symptom_keywords = [
        ent.text for ent in doc.ents if ent.label_ == "SYMPTOM"
    ]
    if symptom_keywords:
        refined_diagnosis += f"You mentioned symptoms like {', '.join(symptom_keywords)}. "
        # ... (You can add logic here to cross-reference symptoms with diseases/pests) ...

    # --- Additional Advice ---
    # (If no clear diagnosis can be made)
    if prediction['disease_probability'] < 0.8 and prediction[
            'pest_probability'] < 0.8:
        refined_diagnosis += "To help me diagnose the issue more accurately, " \
                             "could you please provide more details about the symptoms " \
                             "or any recent changes in the plant's environment?"

    return refined_diagnosis


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Requires authentication
def create_plant_data(request):
    if request.method == 'POST':
        serializer = PlantDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)