"""
Views del módulo Catalog - Productos SmartERP.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .models.products import Productos


@login_required
def lista_productos(request):
    """
    Lista todos los productos con paginación y filtros.
    """
    productos = Productos.objects.all()
    total_sin_filtros = productos.count()
    
    # Filtros de búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        productos = productos.filter(
            Q(title__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(categoria1__icontains=search_query) |
            Q(categoria2__icontains=search_query)
        )
        
        if productos.count() == 0:
            messages.info(request, f'No se encontraron productos con "{search_query}"')
    
    # Filtros por estado
    oferta_filter = request.GET.get('oferta')
    if oferta_filter == 'true':
        productos = productos.filter(oferta=True)
    elif oferta_filter == 'false':
        productos = productos.filter(oferta=False)
        
    stock_filter = request.GET.get('stock')
    if stock_filter == 'disponible':
        productos = productos.filter(sin_stock=False)
    elif stock_filter == 'sin_stock':
        productos = productos.filter(sin_stock=True)
        if productos.count() > 0:
            messages.warning(request, f'Hay {productos.count()} productos sin stock que requieren atención')
    
    # Ordenamiento
    orden = request.GET.get('orden', 'title')
    if orden in ['title', '-title', 'normal_price', '-normal_price', 'brand', '-brand']:
        productos = productos.order_by(orden)
    
    # Paginación
    paginator = Paginator(productos, 25)  # 25 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Últimos productos agregados (para dashboard)
    productos_recientes = Productos.objects.order_by('-datetime')[:5] if hasattr(Productos, 'datetime') else None
    
    context = {
        'productos': page_obj,
        'productos_recientes': productos_recientes,
        'search_query': search_query,
        'total_productos': productos.count(),
        'total_sin_filtros': total_sin_filtros,
        'oferta_filter': oferta_filter,
        'stock_filter': stock_filter,
        'orden': orden,
    }
    
    return render(request, 'catalog/lista_productos.html', context)


@login_required
def crear_producto(request):
    """
    Crear un nuevo producto (solo vista placeholder).
    NOTA: Modelo con managed=False, no se pueden crear registros desde Django.
    """
    if request.method == 'POST':
        messages.error(
            request, 
            'Creación de productos no disponible. '
            'Los productos son administrados externamente.'
        )
        return redirect('catalog:lista_productos')
    
    context = {
        'action': 'Crear',
        'producto': None,
    }
    return render(request, 'catalog/producto_form.html', context)


@login_required
def editar_producto(request, id_producto):
    """
    Editar un producto existente (solo vista placeholder).
    NOTA: Modelo con managed=False, modificaciones limitadas.
    """
    producto = get_object_or_404(Productos, id_producto=id_producto)
    
    if request.method == 'POST':
        messages.warning(
            request,
            'Edición de productos limitada. '
            'Los productos son administrados externamente.'
        )
        return redirect('catalog:lista_productos')
    
    context = {
        'action': 'Editar',
        'producto': producto,
    }
    return render(request, 'catalog/producto_form.html', context)


@login_required
def eliminar_producto(request, id_producto):
    """
    Eliminar un producto (solo vista placeholder).
    NOTA: Modelo con managed=False, no se pueden eliminar registros.
    """
    producto = get_object_or_404(Productos, id_producto=id_producto)
    
    if request.method == 'POST':
        messages.error(
            request,
            'Eliminación de productos no disponible. '
            'Los productos son administrados externamente.'
        )
        return redirect('catalog:lista_productos')
    
    context = {
        'producto': producto,
    }
    return render(request, 'catalog/producto_confirm_delete.html', context)


@login_required
def detalle_producto(request, id_producto):
    """
    Ver detalles de un producto específico.
    """
    producto = get_object_or_404(Productos, id_producto=id_producto)
    
    context = {
        'producto': producto,
    }
    return render(request, 'catalog/detalle_producto.html', context)


# API Views para AJAX
@login_required
def producto_api(request, id_producto):
    """
    API endpoint para obtener datos de producto en JSON.
    """
    try:
        producto = Productos.objects.get(id_producto=id_producto)
        data = {
            'id_producto': producto.id_producto,
            'title': producto.title,
            'brand': producto.brand,
            'normal_price': str(producto.normal_price) if producto.normal_price else None,
            'low_price': str(producto.low_price) if producto.low_price else None,
            'high_price': str(producto.high_price) if producto.high_price else None,
            'oferta': producto.oferta,
            'sin_stock': producto.sin_stock,
            'categoria1': producto.categoria1,
            'categoria2': producto.categoria2,
            'disponible': producto.disponible,
            'oferta_activa': producto.oferta_activa,
        }
        return JsonResponse({'success': True, 'producto': data})
    except Productos.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})