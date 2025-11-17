"""
URLs principales SmartERP con arquitectura modular.
Mantiene compatibilidad con URLs originales usando include().
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps SmartERP - Routing distribuido
    path('', include('inventory.urls')),    # Dashboard raíz
    path('', include('catalog.urls')),      # /productos/*
    path('', include('users.urls')),        # /login/, /logout/
    path('', include('sales.urls')),        # Futuras rutas ventas
]