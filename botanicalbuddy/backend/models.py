from django.db import models
from pgvector.django import VectorField

class PlantData(models.Model):
    trefle_id = models.IntegerField(unique=True, null=True, blank=True)
    common_name = models.CharField(max_length=255, blank=True, null=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    family_common_name = models.CharField(max_length=255, blank=True, null=True)
    family = models.CharField(max_length=255, blank=True, null=True)
    genus = models.CharField(max_length=255, blank=True, null=True)
    growth_habit = models.CharField(max_length=255, blank=True, null=True)
    maximum_height = models.FloatField(blank=True, null=True)
    flower_color = models.CharField(max_length=255, blank=True, null=True)
    native_to = models.JSONField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    care_instructions = models.TextField(blank=True, null=True)
    soil_type = models.CharField(max_length=255, blank=True, null=True)
    water_requirements = models.CharField(max_length=255, blank=True, null=True)
    sunlight_requirements = models.CharField(max_length=255, blank=True, null=True)
    vector_data = VectorField(dimensions=1536, null=True, blank=True)

    # Add the image field for storing uploaded images
    image = models.ImageField(upload_to='plant_images/', blank=True, null=True)

    # Add fields for common diseases and pests (consider using JSONField for more complex data)
    common_diseases = models.JSONField(blank=True, null=True)  
    common_pests = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.common_name or self.scientific_name or f"Plant ID: {self.trefle_id}"

class QAEntry(models.Model):
    plant = models.ForeignKey(PlantData, on_delete=models.CASCADE, related_name='qa_entries')
    question_text = models.TextField()
    question_vector = VectorField(dimensions=1536, null=True, blank=True)
    answer_text = models.TextField()
    answer_vector = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q&A for {self.plant.common_name}: {self.question_text[:50]}..."