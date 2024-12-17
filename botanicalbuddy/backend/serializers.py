# backend/serializers.py
from rest_framework import serializers
from .models import User, VectorDatabase, PlantData, QAEntry

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Include all fields from the User model
        extra_kwargs = {'password': {'write_only': True}}  # Exclude password from responses

class VectorDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorDatabase
        fields = ['id', 'user', 'vector_data', 'name', 'description', 'created_at']

class PlantDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantData
        fields = '__all__'  # Include all fields from the PlantData model
        
class QAEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = QAEntry
        fields = '__all__'  # Or explicitly list the fields
