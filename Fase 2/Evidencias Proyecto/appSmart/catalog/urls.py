"""
URLs del módulo Catalog - Productos.
Mantiene compatibilidad con URLs originales.
"""
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Lista y búsqueda
    path('productos/', views.lista_productos, name='lista_productos'),
    
    # CRUD Productos
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<int:id_producto>/', views.detalle_producto, name='detalle_producto'),
    path('productos/editar/<int:id_producto>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    
    # API JSON (para AJAX)
    path('api/productos/<int:id_producto>/', views.producto_api, name='producto_api'),
]