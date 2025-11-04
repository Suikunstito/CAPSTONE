"""
Servicios del dominio Inventory - Lógica de Stock y Estadísticas
Extrae lógica de negocio de las vistas para reutilización
"""
from django.db.models import Sum, Count
from catalog.models.products import Productos


def get_stock_stats():
    """
    Obtener estadísticas completas de inventario para dashboard
    
    Returns:
        dict: Estadísticas de inventario {
            'total_productos': int,
            'productos_con_stock': int, 
            'productos_sin_stock': int,
            'productos_en_oferta': int,
            'suma_precios': Decimal|None
        }
    """
    return {
        'total_productos': Productos.objects.count(),
        'productos_con_stock': Productos.objects.filter(sin_stock=False).count(),
        'productos_sin_stock': Productos.objects.filter(sin_stock=True).count(),
        'productos_en_oferta': Productos.objects.filter(oferta=True).count(),
        'suma_precios': Productos.objects.aggregate(Sum('normal_price'))['normal_price__sum'],
    }


def get_low_stock_products(threshold=5):
    """
    Obtener productos con stock bajo (funcionalidad futura)
    
    Args:
        threshold (int): Umbral mínimo de stock
        
    Returns:
        QuerySet: Productos con stock bajo
        
    Note:
        # TODO(doc-sync): Implementar cuando se tengan movimientos de inventario
    """
    # Placeholder - requiere tabla de movimientos para calcular stock real
    return Productos.objects.filter(sin_stock=True)


def calculate_inventory_value():
    """
    Calcular valor total del inventario
    
    Returns:
        dict: Valores calculados {
            'total_value': Decimal,
            'average_price': Decimal,
            'products_count': int
        }
    """
    stats = Productos.objects.aggregate(
        total_value=Sum('normal_price'),
        count=Count('id_producto')
    )
    
    avg_price = None
    if stats['total_value'] and stats['count']:
        avg_price = stats['total_value'] / stats['count']
    
    return {
        'total_value': stats['total_value'] or 0,
        'average_price': avg_price,
        'products_count': stats['count'] or 0
    }