# backend/views.py
import logging
import json
import os

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenBlacklistView
from django.http import JsonResponse, HttpResponseForbidden
from asgiref.sync import sync_to_async
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import PlantDataSerializer, QAEntrySerializer, ConversationSerializer, MessageSerializer, UserSerializer
from .models import PlantData as DjangoPlantData, QAEntry, Conversation, Message, User
from .crew import create_crew_with_dynamic_tasks
from .utils import (
    get_plant_by_name,
    create_qa_entry,
    get_similar_qa_entry,
    update_conversation_context,
    sanitize_input,
    validate_input,
    get_embedding,
    extract_plant_name_with_spacy
)

logger = logging.getLogger(__name__)

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
async def ask_botanist(request):
    """Handles user questions about plants using CrewAI."""
    user_query = request.data.get('query', '')
    
    # Input Sanitization and Validation
    try:
        sanitized_query = sanitize_input(user_query)
        validate_input(sanitized_query)
    except ValueError as e:
        logger.warning(f"Invalid user input: {e}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    if not user_query:
        logger.warning("Missing 'query' parameter.")
        return Response({'error': 'Missing query parameter.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Extract potential plant names using spaCy
        plant_name_candidates = extract_plant_name_with_spacy(user_query)

        # Use get_plant_by_name to find the plant in the database
        plant = await get_plant_by_name(plant_name_candidates)
        
        # Check for similar Q&A entry using the identified plant
        question_embedding = get_embedding(user_query)
        if plant and question_embedding:
            similar_qa_entry = await get_similar_qa_entry(plant, question_embedding)
            if similar_qa_entry:
                return Response({'response': similar_qa_entry.answer_text})

        # Create a crew with dynamic tasks
        crew = create_crew_with_dynamic_tasks(user_query)

        # Kick off the crew
        result = crew.kickoff()

        # Update the conversation context (if applicable)
        conversation_id = request.data.get('conversation_id')
        if conversation_id:
            await update_conversation_context(conversation_id, user_query, "user")
            await update_conversation_context(conversation_id, result, "botanist_crew")

        # Create a new Q&A entry if no similar one was found
        if plant:
            await create_qa_entry(plant, user_query, result)

        return Response({'response': result})

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