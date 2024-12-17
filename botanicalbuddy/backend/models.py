# backend/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from pgvector.django import VectorField
from django.core.validators import validate_email, RegexValidator

class User(AbstractUser):
    # Basic Information
    email = models.EmailField(unique=True, validators=[validate_email])
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits.")]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)

    # Profile and Preferences
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    bio = models.TextField(blank=True)
    favorite_plants = models.ManyToManyField('PlantData', blank=True)
    gardening_experience = models.CharField(max_length=50, blank=True)
    preferred_light_conditions = models.CharField(max_length=255, blank=True)
    notification_preferences = models.JSONField(blank=True, null=True)

    # Add related_name to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='backend_user_groups',  # Add related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='backend_user_permissions',  # Add related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

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
    image = models.ImageField(upload_to='plant_images/', blank=True, null=True)
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

class VectorDatabase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vector_data = VectorField(dimensions=1536, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (by {self.user.username})"