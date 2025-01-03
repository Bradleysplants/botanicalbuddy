# backend/urls.py
from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('ask/', views.ask_botanical_question, name='ask_botanical_question'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('plants/', views.create_plant_data, name='create_plant_data'),
    path('plants/<int:pk>/', views.get_plant_data, name='get_plant_data'),
    path('qa_entries/<int:pk>/', views.get_qa_entry, name='get_qa_entry'),
    path('chats/', views.chat_list_create, name='chat_list_create'),
    path('messages/', views.message_create, name='message_create'),
    path('historical-chats/', views.historical_chat_list, name='historical_chat_list'),
    path('chats/<int:pk>/', views.chat_detail, name='chat_detail'),
    path('session/', views.session_view, name='session_view'),
    path('users/me/', views.get_current_user, name='get_current_user'),
]