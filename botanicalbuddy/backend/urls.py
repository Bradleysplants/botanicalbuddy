# backend/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/me/', views.get_current_user, name='get_current_user'),
    path('session/', views.session_view, name='session'),
    path('ask/', views.ask_botanist, name='ask_botanist'),
    path('plants/<int:pk>/', views.get_plant_data, name='get_plant_data'),
    path('plants/', views.create_plant_data, name='create_plant_data'),
    path('chats/', views.chat_list_create, name='chat_list_create'),
    path('messages/', views.message_create, name='message_create'),
    path('history/', views.historical_chat_list, name='historical_chat_list'),
    path('chats/<int:pk>/', views.chat_detail, name='chat_detail'),
]