"""
URLs principales del proyecto SmartERP - Arquitectura modular
Migrado de estructura monolítica a apps por dominio
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas por dominio (nueva arquitectura modular)
    path('', include('inventory.urls')),        # Dashboard en raíz
    path('', include('catalog.urls')),          # CRUD productos (/productos/)
    path('', include('users.urls')),            # Auth (/login/, /logout/)
    path('', include('sales.urls')),            # Ventas (futuro)
    
    # Compatibilidad: mantener estructura de URLs original
    # path('', include('productos.urls')),  # ❌ REMOVIDO tras migración
]
