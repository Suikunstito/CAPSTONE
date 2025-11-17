"""
Views del módulo Inventory - Dashboard y Predicciones SmartERP.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Sum, Avg, Max, Min
from django.utils import timezone
import csv
import json

from catalog.models.products import Productos
from sales.models.sales import Ventas
from .services.predictions import generar_predicciones


@login_required
def home(request):
    """
    Dashboard principal de SmartERP - Vista raíz.
    """
    return dashboard(request)


@login_required
def dashboard(request):
    """
    Dashboard principal con estadísticas y gráficos de inventario.
    """
    # Estadísticas básicas de productos
    total_productos = Productos.objects.count()
    productos_con_stock = Productos.objects.filter(sin_stock=False).count()
    productos_sin_stock = Productos.objects.filter(sin_stock=True).count()
    productos_oferta = Productos.objects.filter(oferta=True).count()
    
    # Estadísticas de precios
    precios_stats = Productos.objects.filter(normal_price__isnull=False).aggregate(
        precio_promedio=Avg('normal_price'),
        precio_max=Max('normal_price'),
        precio_min=Min('normal_price')
    )
    
    # Top categorías
    categorias_top = Productos.objects.filter(
        categoria1__isnull=False
    ).values('categoria1').annotate(
        count=Count('categoria1')
    ).order_by('-count')[:5]
    
    # Top marcas
    marcas_top = Productos.objects.filter(
        brand__isnull=False
    ).values('brand').annotate(
        count=Count('brand')
    ).order_by('-count')[:5]
    
    # Ventas recientes (si hay datos)
    try:
        ventas_recientes = Ventas.objects.select_related('id_producto').order_by('-fecha')[:10]
        total_ventas = Ventas.objects.aggregate(
            total_cantidad=Sum('cantidad_vendida'),
            total_ingresos=Sum('total_venta')
        )
    except:
        ventas_recientes = []
        total_ventas = {'total_cantidad': 0, 'total_ingresos': 0}
    
    # Productos con predicción de compra
    try:
        predicciones_data = generar_predicciones()
        productos_recomendados = predicciones_data.sugerencias
    except:
        productos_recomendados = 0
    
    # Preparar datos para gráficos (Chart.js)
    chart_data = {
        'stock_distribution': {
            'labels': ['Con Stock', 'Sin Stock'],
            'data': [productos_con_stock, productos_sin_stock]
        },
        'categorias_top': {
            'labels': [cat['categoria1'][:20] for cat in categorias_top],
            'data': [cat['count'] for cat in categorias_top]
        },
        'marcas_top': {
            'labels': [marca['brand'][:15] for marca in marcas_top],
            'data': [marca['count'] for marca in marcas_top]
        }
    }
    
    # Productos recientes
    productos_recientes = Productos.objects.order_by('-datetime')[:5] if hasattr(Productos, 'datetime') else Productos.objects.all()[:5]
    
    # Mostrar alertas automáticas
    if productos_sin_stock > 10:
        messages.warning(request, f'⚠️ Atención: {productos_sin_stock} productos sin stock')
    
    context = {
        'total_productos': total_productos,
        'productos_con_stock': productos_con_stock,
        'productos_sin_stock': productos_sin_stock,
        'productos_oferta': productos_oferta,
        'productos_recomendados': productos_recomendados,
        'productos_recientes': productos_recientes,
        'precios_stats': precios_stats,
        'categorias_top': categorias_top,
        'marcas_top': marcas_top,
        'ventas_recientes': ventas_recientes,
        'total_ventas': total_ventas,
        'chart_data_json': json.dumps(chart_data),
        'fecha_actual': timezone.now(),
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def prediccion_productos(request):
    """
    Vista de predicciones ML para recomendaciones de compra.
    """
    try:
        # Obtener predicciones usando el sistema de ML
        predicciones_data = generar_predicciones()
        productos_prediccion = predicciones_data.items
        
        prediction_summary = {
            'total_productos': len(productos_prediccion),
            'productos_recomendados': predicciones_data.sugerencias,
            'productos_sobrestock': predicciones_data.sobrestock,
            'promedio_probabilidad': sum(p.probabilidad for p in productos_prediccion) / len(productos_prediccion) if productos_prediccion else 0
        }
        
        # Filtros opcionales
        accion_filter = request.GET.get('accion')
        if accion_filter and accion_filter in ['comprar', 'mantener', 'evaluar']:
            productos_prediccion = [
                p for p in productos_prediccion 
                if p.accion.lower() == accion_filter
            ]
        
        # Ordenamiento
        orden = request.GET.get('orden', 'probabilidad')
        if orden == 'probabilidad':
            productos_prediccion.sort(key=lambda x: x.probabilidad, reverse=True)
        elif orden == 'tendencia':
            productos_prediccion.sort(key=lambda x: x.tendencia, reverse=True)
        elif orden == 'volatilidad':
            productos_prediccion.sort(key=lambda x: x.volatilidad)
    
    except Exception as e:
        productos_prediccion = []
        prediction_summary = {
            'total_productos': 0,
            'productos_recomendados': 0,
            'promedio_probabilidad': 0,
            'error': str(e)
        }
    
    context = {
        'productos_prediccion': productos_prediccion[:50],  # Limitar a 50 resultados
        'prediction_summary': prediction_summary,
        'accion_filter': accion_filter,
        'orden': orden,
        'total_resultados': len(productos_prediccion),
    }
    
    return render(request, 'inventory/predicciones.html', context)


@login_required
def informes(request):
    """
    Panel de informes y reportes descargables.
    """
    # Estadísticas para los informes
    informes_stats = {
        'productos_total': Productos.objects.count(),
        'productos_activos': Productos.objects.filter(sin_stock=False).count(),
        'categorias_unicas': Productos.objects.values('categoria1').distinct().count(),
        'marcas_unicas': Productos.objects.values('brand').distinct().count(),
    }
    
    try:
        informes_stats.update({
            'ventas_total': Ventas.objects.count(),
            'ventas_ultimo_mes': Ventas.objects.filter(
                fecha__gte=timezone.now().date() - timezone.timedelta(days=30)
            ).count(),
        })
    except:
        informes_stats.update({
            'ventas_total': 0,
            'ventas_ultimo_mes': 0,
        })
    
    context = {
        'informes_stats': informes_stats,
        'fecha_generacion': timezone.now(),
    }
    
    return render(request, 'inventory/informes.html', context)


@login_required
def exportar_reporte_compras(request):
    """
    Exportar reporte de productos recomendados para compra en CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_compras.csv"'
    response.write('\ufeff')  # BOM para UTF-8
    
    writer = csv.writer(response)
    writer.writerow([
        'ID Producto', 'Título', 'Marca', 'Precio Referencia',
        'Probabilidad Compra', 'Tendencia', 'Acción', 'Motivo',
        'Cantidad Sugerida', 'Stock Estimado'
    ])
    
    try:
        predicciones_data = generar_predicciones()
        # Solo productos con acción de compra
        productos_compra = [p for p in predicciones_data.items if p.accion.lower() == 'comprar']
        
        for producto in productos_compra:
            writer.writerow([
                producto.producto.id_producto,
                producto.producto.title,
                producto.producto.brand or 'Sin marca',
                producto.precio_referencia,
                f"{producto.probabilidad_pct:.1f}%",
                producto.tendencia,
                producto.accion,
                producto.motivo,
                producto.cantidad_sugerida,
                producto.stock_estimado,
            ])
            
    except Exception as e:
        writer.writerow(['Error al generar reporte:', str(e)])
    
    return response


@login_required
def exportar_reporte_stock(request):
    """
    Exportar resumen completo de stock en CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="resumen_stock.csv"'
    response.write('\ufeff')  # BOM para UTF-8
    
    writer = csv.writer(response)
    writer.writerow([
        'ID Producto', 'Título', 'Marca', 'Categoría 1', 'Categoría 2',
        'Precio Normal', 'En Oferta', 'Sin Stock', 'Disponible'
    ])
    
    productos = Productos.objects.all().order_by('categoria1', 'title')
    
    for producto in productos:
        writer.writerow([
            producto.id_producto,
            producto.title,
            producto.brand or 'Sin marca',
            producto.categoria1 or 'Sin categoría',
            producto.categoria2 or 'Sin subcategoría',
            producto.normal_price or 0,
            'Sí' if producto.oferta else 'No',
            'Sí' if producto.sin_stock else 'No',
            'Sí' if producto.disponible else 'No',
        ])
    
    return response


# Importar modelo faltante para dashboard
from django.db.models import Max, Min