from django.urls import path
from . import views

urlpatterns = [
    path('ask_question/', views.ask_botanical_question, name='ask_question'),  # Updated URL pattern
    path('upload_image/', views.upload_image, name='upload_image'),  # Add the new endpoint
]