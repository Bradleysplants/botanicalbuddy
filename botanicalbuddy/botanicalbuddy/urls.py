from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from backend import views

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include('backend.urls')), 
    path('session/', views.session_view, name='session_view'),
]