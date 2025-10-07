from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:id_producto>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
]

