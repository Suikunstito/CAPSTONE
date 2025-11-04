"""
URLs del dominio Catalog - CRUD de Productos
Mantiene las URLs originales para compatibilidad
"""
from django.urls import path
from catalog.views import products

urlpatterns = [
    path('productos/', products.lista_productos, name='productos'),
    path('productos/nuevo/', products.crear_producto, name='crear_producto'),
    path('productos/editar/<int:id_producto>/', products.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', products.eliminar_producto, name='eliminar_producto'),
]