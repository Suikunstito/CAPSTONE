"""
URLs del módulo Inventory - Dashboard y Predicciones.
"""
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),  # Dashboard raíz
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Predicciones e Informes
    path('predicciones/', views.prediccion_productos, name='predicciones'),
    path('movimientos/', views.informes, name='movimientos'),  # Alias para movimientos
    path('informes/', views.informes, name='informes'),
    
    # Exportación de reportes
    path('informes/reporte-compras.csv', views.exportar_reporte_compras, name='reporte_compras_csv'),
    path('informes/resumen-stock.csv', views.exportar_reporte_stock, name='reporte_stock_csv'),
]