# backend/serializers.py
from rest_framework import serializers
from .models import User, VectorDatabase, PlantData, QAEntry, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']  # Include necessary fields
        extra_kwargs = {'password': {'write_only': True}}

class VectorDatabaseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Display user details
    class Meta:
        model = VectorDatabase
        fields = ['id', 'user', 'vector_data', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

class PlantDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantData
        fields = '__all__'

class QAEntrySerializer(serializers.ModelSerializer):
    plant = PlantDataSerializer(read_only=True)  # Display plant details
    class Meta:
        model = QAEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'plant']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at']
        read_only_fields = ['id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'timestamp', 'sender', 'conversation']