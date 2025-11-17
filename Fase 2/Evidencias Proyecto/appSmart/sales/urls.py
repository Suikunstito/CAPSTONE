"""
URLs del módulo Sales - Ventas y transacciones.
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Futuras rutas de ventas
    # path('ventas/', views.lista_ventas, name='lista_ventas'),
    # path('usuarios/', views.usuarios, name='usuarios'),  # Temporal aquí hasta crear users management
]