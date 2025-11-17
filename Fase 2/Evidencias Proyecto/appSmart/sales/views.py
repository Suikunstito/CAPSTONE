"""
Views del módulo Sales - Ventas y transacciones SmartERP.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone

from .models.sales import Ventas
from catalog.models.products import Productos


# =================================================================
# PLACEHOLDER VIEWS - Preparadas para expansión futura
# =================================================================

@login_required
def lista_ventas(request):
    """
    Listar todas las ventas con filtros y paginación.
    PLACEHOLDER: Preparado para implementación futura.
    """
    # TODO: Implementar cuando se requiera gestión completa de ventas
    ventas = Ventas.objects.select_related('id_producto').order_by('-fecha')
    
    context = {
        'ventas': ventas,
        'total_ventas': ventas.count(),
        'placeholder_mode': True,
        'mensaje': 'Módulo de ventas en desarrollo - Vista placeholder'
    }
    
    return render(request, 'sales/lista_ventas.html', context)


@login_required
def detalle_venta(request, id_venta):
    """
    Ver detalle de una venta específica.
    PLACEHOLDER: Preparado para implementación futura.
    """
    try:
        venta = Ventas.objects.select_related('id_producto').get(id_venta=id_venta)
    except Ventas.DoesNotExist:
        venta = None
    
    context = {
        'venta': venta,
        'placeholder_mode': True,
        'mensaje': 'Vista de detalle de ventas - Funcionalidad en desarrollo'
    }
    
    return render(request, 'sales/detalle_venta.html', context)


@login_required 
def reportes_ventas(request):
    """
    Dashboard de reportes de ventas.
    PLACEHOLDER: Preparado para análisis avanzado futuro.
    """
    try:
        stats = {
            'total_ventas': Ventas.objects.count(),
            'ventas_hoy': Ventas.objects.filter(fecha=timezone.now().date()).count(),
            'ingresos_total': Ventas.objects.aggregate(total=Sum('total_venta'))['total'] or 0,
            'producto_mas_vendido': Ventas.objects.values(
                'id_producto__title'
            ).annotate(
                total_cantidad=Sum('cantidad_vendida')
            ).order_by('-total_cantidad').first()
        }
    except:
        stats = {
            'total_ventas': 0,
            'ventas_hoy': 0,
            'ingresos_total': 0,
            'producto_mas_vendido': None
        }
    
    context = {
        'stats': stats,
        'placeholder_mode': True,
        'mensaje': 'Sistema de reportes de ventas en desarrollo'
    }
    
    return render(request, 'sales/reportes_ventas.html', context)


# =================================================================
# GESTIÓN DE USUARIOS (Temporal hasta crear app users management)
# =================================================================

@login_required
def usuarios(request):
    """
    Gestión básica de usuarios.
    TEMPORAL: Migrar a app users cuando se expanda funcionalidad.
    """
    from django.contrib.auth.models import User
    
    usuarios = User.objects.all().order_by('username')
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
        'placeholder_mode': True,
        'mensaje': 'Gestión básica de usuarios - Expandir funcionalidad futura'
    }
    
    return render(request, 'sales/usuarios.html', context)