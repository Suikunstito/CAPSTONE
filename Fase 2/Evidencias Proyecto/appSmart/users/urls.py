"""
URLs del dominio Users - Autenticación
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from users.views.auth import CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]