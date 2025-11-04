"""
URLs del dominio Inventory - Dashboard y Estadísticas
"""
from django.urls import path
from inventory.views.dashboard import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Ruta raíz mantiene dashboard
]