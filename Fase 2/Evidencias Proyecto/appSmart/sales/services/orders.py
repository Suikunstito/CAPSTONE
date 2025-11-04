"""
Servicios del dominio Sales - Lógica de Ventas y Transacciones  
Funcionalidad futura para registro completo de ventas
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from catalog.models.products import Productos
from sales.models.sales import Ventas


def register_sale(producto_id, cantidad, precio_unitario):
    """
    Registrar una venta completa con validaciones
    
    Args:
        producto_id (int): ID del producto vendido
        cantidad (int): Cantidad vendida
        precio_unitario (Decimal): Precio por unidad
        
    Returns:
        Ventas: Instancia de venta creada
        
    Raises:
        ValueError: Si el producto no existe o datos inválidos
    """
    # Validar producto existe
    try:
        producto = Productos.objects.get(id_producto=producto_id)
    except Productos.DoesNotExist:
        raise ValueError(f"Producto {producto_id} no existe")
    
    # Validar cantidad y precio
    if cantidad <= 0:
        raise ValueError("Cantidad debe ser mayor a 0")
    if precio_unitario <= 0:
        raise ValueError("Precio unitario debe ser mayor a 0")
    
    # Calcular total
    total = cantidad * precio_unitario
    
    # Crear venta en transacción
    with transaction.atomic():
        venta = Ventas.objects.create(
            id_producto=producto,
            fecha=timezone.now().date(),
            cantidad_vendida=cantidad,
            precio_unitario=precio_unitario,
            total_venta=total
        )
        
        # TODO(doc-sync): Aquí se podría actualizar stock automáticamente
        # si se implementa tabla de movimientos de inventario
        
        return venta


def get_sales_summary(fecha_desde=None, fecha_hasta=None):
    """
    Obtener resumen de ventas por período
    
    Args:
        fecha_desde (date, optional): Fecha inicio filtro
        fecha_hasta (date, optional): Fecha fin filtro
        
    Returns:
        dict: Resumen de ventas {
            'total_ventas': int,
            'total_ingresos': Decimal,
            'productos_vendidos': int
        }
    """
    queryset = Ventas.objects.all()
    
    if fecha_desde:
        queryset = queryset.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(fecha__lte=fecha_hasta)
    
    from django.db.models import Sum, Count
    summary = queryset.aggregate(
        total_ventas=Count('id_venta'),
        total_ingresos=Sum('total_venta'),
        productos_vendidos=Sum('cantidad_vendida')
    )
    
    return {
        'total_ventas': summary['total_ventas'] or 0,
        'total_ingresos': summary['total_ingresos'] or Decimal('0.00'),
        'productos_vendidos': summary['productos_vendidos'] or 0
    }


def get_top_selling_products(limit=10):
    """
    Obtener productos más vendidos
    
    Args:
        limit (int): Número máximo de productos a retornar
        
    Returns:
        QuerySet: Productos ordenados por cantidad vendida
    """
    # TODO(doc-sync): Implementar aggregation por producto
    # Requiere GROUP BY en Ventas.id_producto
    return Productos.objects.all()[:limit]