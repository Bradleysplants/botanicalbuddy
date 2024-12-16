from rest_framework import serializers
from .models import User, VectorDatabase, PlantData

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class VectorDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorDatabase
        fields = ['id', 'user', 'vector_data', 'name', 'description', 'created_at']

class PlantDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantData
        fields = ['id', 'plant_name', 'scientific_name', 'description', 'care_instructions', 'soil_type', 'water_requirements', 'sunlight_requirements', 'created_at']
