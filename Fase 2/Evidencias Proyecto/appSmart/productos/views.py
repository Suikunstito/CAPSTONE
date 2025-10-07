from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth.views import LoginView
from .models import Productos
from .forms import ProductoForm


# DASHBOARD / INICIO
@login_required
def dashboard(request):
    total_productos = Productos.objects.count()
    productos_con_stock = Productos.objects.filter(sin_stock=False).count()
    productos_sin_stock = Productos.objects.filter(sin_stock=True).count()
    productos_en_oferta = Productos.objects.filter(oferta=True).count()
    promedio_precio = Productos.objects.aggregate(Sum('normal_price'))['normal_price__sum']

    context = {
        'total_productos': total_productos,
        'productos_con_stock': productos_con_stock,
        'productos_sin_stock': productos_sin_stock,
        'productos_en_oferta': productos_en_oferta,
        'promedio_precio': promedio_precio,
    }
    return render(request, 'dashboard.html', context)


@login_required
def lista_productos(request):
    productos = Productos.objects.all().order_by('-id_producto')  # Mostrar todos, más recientes primero
    return render(request, 'productos.html', {'productos': productos})


# CREAR PRODUCTO
@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'producto_form.html', {'form': form, 'accion': 'Agregar Producto'})


# EDITAR PRODUCTO
@login_required
def editar_producto(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'producto_form.html', {'form': form, 'accion': 'Editar Producto'})


# ELIMINAR PRODUCTO
@login_required
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos')
    return render(request, 'producto_confirm_delete.html', {'producto': producto})


# LOGIN PERSONALIZADO
class CustomLoginView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
