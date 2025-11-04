"""
Vistas del dominio Catalog - CRUD de Productos
Migrado desde productos/views.py (lista_productos, crear_producto, editar_producto, eliminar_producto)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from catalog.models.products import Productos
from catalog.forms.products import ProductoForm


@login_required
def lista_productos(request):
    """Lista todos los productos ordenados por más recientes"""
    productos = Productos.objects.all().order_by('-id_producto')  # Mantener orden original
    return render(request, 'catalog/productos.html', {'productos': productos})


@login_required
def crear_producto(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')  # Mantener nombre de URL original
    else:
        form = ProductoForm()
    return render(request, 'catalog/producto_form.html', {'form': form, 'accion': 'Agregar Producto'})


@login_required
def editar_producto(request, id_producto):
    """Editar producto existente usando PK personalizada"""
    producto = get_object_or_404(Productos, id_producto=id_producto)  # PK personalizada mantenida
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'catalog/producto_form.html', {'form': form, 'accion': 'Editar Producto'})


@login_required
def eliminar_producto(request, id_producto):
    """Eliminar producto con confirmación"""
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos')
    return render(request, 'catalog/producto_confirm_delete.html', {'producto': producto})