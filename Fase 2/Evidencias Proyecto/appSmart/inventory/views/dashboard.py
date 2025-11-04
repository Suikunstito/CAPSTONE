"""
Vistas del dominio Inventory - Dashboard y Estadísticas
Migrado desde productos/views.py (función dashboard)
Ahora usa servicios para separar lógica de negocio
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inventory.services.stock import get_stock_stats


@login_required
def dashboard(request):
    """
    Dashboard principal con estadísticas de inventario
    Usa servicios para obtener estadísticas y mantener vistas ligeras
    """
    stats = get_stock_stats()
    
    context = {
        'total_productos': stats['total_productos'],
        'productos_con_stock': stats['productos_con_stock'],
        'productos_sin_stock': stats['productos_sin_stock'],
        'productos_en_oferta': stats['productos_en_oferta'],
        'promedio_precio': stats['suma_precios'],  # Mantener nombre original para compatibilidad template
    }
    return render(request, 'inventory/dashboard.html', context)