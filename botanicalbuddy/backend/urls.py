from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('ask_botanical_question/', views.ask_botanical_question, name='ask_botanical_question'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('create_plant_data/', views.create_plant_data, name='create_plant_data'),
    path('get_plant_data/<int:pk>/', views.get_plant_data, name='get_plant_data'),
    path('create_qa_entry/', views.create_qa_entry, name='create_qa_entry'),
    path('get_qa_entry/<int:pk>/', views.get_qa_entry, name='get_qa_entry'),
    path('session/', views.session_view, name='session_view'),
    # ... other URL patterns ...
]