from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:id_producto>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('predicciones/', views.prediccion_productos, name='prediccion_productos'),
    path('informes/', views.informes, name='informes'),
    path('informes/reporte-compras.csv', views.exportar_reporte_compras, name='reporte_compras_csv'),
    path('informes/resumen-stock.csv', views.exportar_reporte_stock, name='reporte_stock_csv'),
    path('usuarios/', views.usuarios, name='usuarios'),
]
