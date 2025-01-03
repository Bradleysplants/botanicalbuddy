# backend/views.py
import logging
import json
import os
from io import BytesIO

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenBlacklistView
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from django.db.models import F, Q
import spacy
import numpy as np
from PIL import Image
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken  # Import for JWT

from .serializers import PlantDataSerializer, QAEntrySerializer, ConversationSerializer, MessageSerializer, UserSerializer
from .models import PlantData as DjangoPlantData, QAEntry, Conversation, Message
from .pydanticai import PlantData, create_agent, InferenceResult, AIAgent
from .utils import calculate_cosine_similarity, get_embedding

logger = logging.getLogger(__name__)
agent: AIAgent = create_agent()
nlp = spacy.load("en_core_web_sm")

# --- Intent Keywords (Lowercase Lemmas) ---
DIAGNOSE_KEYWORDS = [
    "why be",
    "what be wrong with",
    "problem with",
    "issue with",
    "my plant have",
    "leaf be",
    "spot on",
    "turn yellow",
    "turn brown",
    "wilt",
    "droop",
    "die",
    "sick",
    "unhealthy",
    "pest on",
    "bug on",
    "insect on",
    "disease on",
    "affect by",
    "show sign of"
]
TREATMENT_KEYWORDS = [
    "how to fix",
    "how to get rid of",
    "how to treat",
    "cure for",
    "remedy for",
    "best way to remove",
    "what can i do about",
    "solution for",
    "help with",
    "prevent",
    "control",
    "eliminate"
]
CARE_KEYWORDS = [
    "how to care for",
    "how to grow",
    "care tip for",
    "water",
    "light for",
    "soil for",
    "fertilize",
    "repot",
    "sunlight",
    "humidity for",
    "best condition for",
    "need",
    "requirement",
    "should i",
    "can i",
    "do they need"
]

# --- Helper Functions ---
def find_closest_match_nlp(text, options):
    """Finds the closest matching string from a list using spaCy."""
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
    """Retrieves a similar Q&A entry from the database."""
    qa_entries = await QAEntry.objects.filter(plant=plant).aall()
    for entry in qa_entries:
        similarity = calculate_cosine_similarity(question_vector, entry.question_vector)
        if similarity >= threshold:
            return entry
    return None

@sync_to_async
def create_qa_entry(plant, question_text, question_vector, answer_text):
    """Creates a new Q&A entry in the database."""
    QAEntry.objects.create(plant=plant,
                           question_text=question_text,
                           question_vector=question_vector,
                           answer_text=answer_text)

def refine_diagnosis(prediction, plant_name, common_diseases, common_pests, user_query):
    """Refines the initial prediction by combining it with other information."""
    refined_diagnosis = f"Based on the image analysis and your query, "

    if prediction.get('disease_probability', 0) > 0.8 and prediction.get('disease_label'):
        predicted_disease = prediction['disease_label']
        if predicted_disease in common_diseases:
            refined_diagnosis += f"it seems like your {plant_name} might have {predicted_disease}. "
        else:
            refined_diagnosis += f"it seems like your {plant_name} might have a disease similar to {predicted_disease}. "
    else:
        refined_diagnosis += "I couldn't confidently identify a specific disease. "

    if prediction.get('pest_probability', 0) > 0.8 and prediction.get('pest_label'):
        predicted_pest = prediction['pest_label']
        if predicted_pest in common_pests:
            refined_diagnosis += f"I also noticed signs of {predicted_pest}. "
        else:
            refined_diagnosis += f"I also noticed signs of a pest similar to {predicted_pest}. "

    doc = nlp(user_query)
    symptom_keywords = [ent.text for ent in doc.ents if ent.label_ == "SYMPTOM"]
    if symptom_keywords:
        refined_diagnosis += f"You mentioned symptoms like {', '.join(symptom_keywords)}. "

    if prediction.get('disease_probability', 0) < 0.8 and prediction.get('pest_probability', 0) < 0.8:
        refined_diagnosis += "To help me diagnose the issue more accurately, " \
                             "could you please provide more details about the symptoms " \
                             "or any recent changes in the plant's environment?"

    return refined_diagnosis

# --- API Endpoints ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {'username': user.username, 'email': user.email},
        }, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    try:
        refresh_token = request.data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def session_view(request):
    """Returns session data if available."""
    username = request.session.get('username')
    return Response({'username': username} if username else {'message': 'No session data found'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def upload_image(request):
    """Uploads an image for plant analysis and integrates with a model API."""
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']
    plant_id = request.POST.get('plant_id')

    try:
        plant = await DjangoPlantData.objects.aget(id=plant_id)
    except DjangoPlantData.DoesNotExist:
        return JsonResponse({'error': 'Plant not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Save the image to the PlantData model
        plant.image = image_file
        await sync_to_async(plant.save)()

        # Preprocess the image and prepare for model API
        image = Image.open(image_file)
        image = image.resize((224, 224))
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        # Make request to the model API (replace with your actual endpoint)
        model_api_url = "your_openai_model_api_endpoint"
        response = requests.post(model_api_url, files={'image': image_bytes})
        response.raise_for_status()
        prediction_results = response.json()

        return JsonResponse({'status': 'success', 'prediction': prediction_results})

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with the model API: {e}")
        return JsonResponse({'error': 'Failed to get a prediction from the model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.exception(f"Unexpected error in upload_image: {e}")
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qa_entry(request, pk):
    """Retrieves a specific Q&A entry."""
    qa_entry = get_object_or_404(QAEntry, pk=pk)
    serializer = QAEntrySerializer(qa_entry)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def ask_botanical_question(request):
    """Handles user questions about plants, incorporating NLP for intent recognition."""
    user_query = request.data.get('query', '')
    similarity_threshold = float(os.environ.get("SIMILARITY_THRESHOLD", 0.75))

    if not user_query:
        logger.warning("Missing 'query' parameter.")
        return Response({'error': 'Missing query parameter.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # --- Extract plant name from the query using NLP ---
        doc = nlp(user_query)
        plant_name = None
        for ent in doc.ents:
            # This is a basic approach; you might need a more specific NER model for plants
            if ent.label_ in ["PLANT", "FLOWER", "GARDEN_PLANT"]:  # Example entity labels
                plant_name = ent.text
                break

        if not plant_name:
            # Fallback: look for capitalized words (basic heuristic)
            for token in doc:
                if token.is_title and not token.is_stop:
                    plant_name = token.text
                    break

        if not plant_name:
            logger.warning(f"Could not identify plant name in query: '{user_query}'")
            return Response({'error': "Could you please specify the name of the plant you are asking about?"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to find the plant in the database
        django_plant = await DjangoPlantData.objects.filter(
            Q(common_name__iexact=plant_name) | Q(scientific_name__iexact=plant_name)
        ).afirst()

        if not django_plant:
            plant_names = [plant.common_name for plant in await DjangoPlantData.objects.aall()]
            closest_match = find_closest_match_nlp(plant_name, plant_names)
            if closest_match:
                django_plant = await DjangoPlantData.objects.aget(common_name=closest_match)
            else:
                logger.warning(f"Plant '{plant_name}' not found.")
                return Response({'error': f"Plant '{plant_name}' not found in our database."}, status=status.HTTP_404_NOT_FOUND)

        # --- Intent Recognition using Lemmatization ---
        intent = None
        doc = nlp(user_query.lower())
        lemmas = [token.lemma_ for token in doc]  # Get the lemmas of the tokens

        if any(lemma in DIAGNOSE_KEYWORDS for lemma in lemmas):
            intent = "diagnose_problem"
        elif any(lemma in TREATMENT_KEYWORDS for lemma in lemmas):
            intent = "suggest_treatment"
        elif any(lemma in CARE_KEYWORDS for lemma in lemmas):
            intent = "general_care"

        logger.info(f"Detected intent (lemmas): {intent}")

        if intent == "diagnose_problem":
            return Response({'answer': f"You're asking about a problem with your {django_plant.common_name}. "
                                      f"Can you describe the symptoms in more detail?"})
        elif intent == "suggest_treatment":
            return Response({'answer': f"You're looking for treatment advice for your {django_plant.common_name}. "
                                      f"What issue are you trying to address?"})
        elif intent == "general_care":
            return Response({'answer': f"You're asking for general care tips for your {django_plant.common_name}. "
                                      f"What specifically would you like to know (e.g., watering, light, soil)?"})
        else:
            # --- Fallback to AI Agent ---
            plant_data = PlantData(
                plant_name=django_plant.common_name,
                scientific_name=django_plant.scientific_name,
                description=django_plant.description,
                care_instructions=django_plant.care_instructions,
                soil_type=django_plant.soil_type,
                water_requirements=django_plant.water_requirements,
                sunlight_requirements=django_plant.sunlight_requirements,
            )
            inference_result = await agent.run_inference(plant_data, user_query)
            if isinstance(inference_result, InferenceResult):
                answer = inference_result.answer
                await create_qa_entry(django_plant, user_query, None, answer) # Consider generating embedding for ollama too
                return Response({'answer': answer})
            else:
                logger.error(f"Inference failed: {inference_result}")
                return Response({'error': 'Failed to generate an answer.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON data received: {request.body}")
        return Response({'error': 'Invalid JSON data in request body.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_plant_data(request, pk):
    """Retrieves specific plant data."""
    plant = get_object_or_404(DjangoPlantData, pk=pk)
    serializer = PlantDataSerializer(plant)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_plant_data(request):
    """Creates new plant data."""
    serializer = PlantDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_list_create(request):
    """
    GET: Lists all conversations for the authenticated user.
    POST: Creates a new conversation.
    """
    if request.method == 'GET':
        conversations = request.user.conversations.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response({'chats': serializer.data})

    elif request.method == 'POST':
        plant_name = request.data.get('plant_name')
        if not plant_name:
            return Response({'error': 'Plant name is required to start a chat.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plant = DjangoPlantData.objects.get(common_name=plant_name)
        except DjangoPlantData.DoesNotExist:
            return Response({'error': 'Plant not found.'}, status=status.HTTP_404_NOT_FOUND)

        existing_conversation = request.user.conversations.filter().first() # Consider filtering by plant as well
        if existing_conversation:
            serializer = ConversationSerializer(existing_conversation)
            return Response({'chat': serializer.data}, status=status.HTTP_200_OK)
        else:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user)
            # Optionally link the conversation to the plant: conversation.plant = plant
            serializer = ConversationSerializer(conversation)
            return Response({'chat': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def message_create(request):
    """Creates a new message in a conversation."""
    conversation_id = request.data.get('chat_id')
    text = request.data.get('text')

    if not conversation_id or not text:
        return Response({'error': 'Chat ID and message text are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        conversation = await Conversation.objects.aget(id=conversation_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Chat not found or you are not a participant.'}, status=status.HTTP_404_NOT_FOUND)

    message = await Message.objects.acreate(conversation=conversation, sender=request.user, content=text)
    serializer = MessageSerializer(message)
    return Response({'message': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historical_chat_list(request):
    """Lists all past conversations for the authenticated user."""
    conversations = request.user.conversations.all().order_by('-created_at')
    serializer = ConversationSerializer(conversations, many=True)
    return Response({'chats': serializer.data})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_detail(request, pk):
    """Retrieves a specific conversation with its messages."""
    try:
        conversation = Conversation.objects.get(pk=pk, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Chat not found or you are not a participant.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ConversationSerializer(conversation)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
    message_serializer = MessageSerializer(messages, many=True)

    response_data = serializer.data
    response_data['messages'] = message_serializer.data
    return Response({'chat': response_data})