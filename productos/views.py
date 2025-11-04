import csv
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm
from .models import Productos
from .predicciones import (
    exportar_reporte_compras_csv,
    exportar_reporte_stock_csv,
    generar_predicciones,
)


def _user_is_admin(user):
    return user.is_superuser or user.is_staff


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if _user_is_admin(request.user):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'No tienes permisos para acceder a esta seccion.')
        return redirect('home')

    return _wrapped


def _valor_positivo(value):
    try:
        return value is not None and float(value) > 0
    except (TypeError, ValueError):
        return False


def _analizar_producto(producto):
    tiene_precio = any(
        _valor_positivo(valor)
        for valor in (producto.normal_price, producto.low_price, producto.high_price)
    )
    oferta_activa = bool(producto.oferta) or any(
        _valor_positivo(valor)
        for valor in (producto.ahorro, producto.ahorro_percent)
    )
    inconsistente = bool(producto.sin_stock) and tiene_precio
    return tiene_precio, oferta_activa, inconsistente


def _calcular_metricas(productos, decorar=False):
    total = 0
    disponibles = 0
    en_oferta = 0
    inconsistentes = 0

    for producto in productos:
        total += 1
        disponible, oferta_activa, inconsistente = _analizar_producto(producto)
        if decorar:
            producto.disponible = disponible
            producto.oferta_activa = oferta_activa
            producto.stock_inconsistente = inconsistente
        if disponible:
            disponibles += 1
        if oferta_activa:
            en_oferta += 1
        if inconsistente:
            inconsistentes += 1

    return {
        'total': total,
        'disponibles': disponibles,
        'sin_stock': max(total - disponibles, 0),
        'en_oferta': en_oferta,
        'inconsistentes': inconsistentes,
    }


@login_required
def home(request):
    context = {'is_admin': _user_is_admin(request.user)}
    return render(request, 'home.html', context)


@login_required
@admin_required
def dashboard(request):
    productos_lista = list(Productos.objects.all())
    metricas_inventario = _calcular_metricas(productos_lista, decorar=False)
    stats = Productos.objects.aggregate(
        suma=Sum('normal_price'),
        promedio=Avg('normal_price'),
    )

    predicciones_payload = generar_predicciones()

    context = {
        'total_productos': metricas_inventario['total'],
        'productos_con_stock': metricas_inventario['disponibles'],
        'productos_sin_stock': metricas_inventario['sin_stock'],
        'productos_en_oferta': metricas_inventario['en_oferta'],
        'productos_inconsistentes': metricas_inventario['inconsistentes'],
        'promedio_precio': stats['promedio'],
        'suma_precio': stats['suma'],
        'pred_sugerencias': predicciones_payload.sugerencias,
        'pred_sobrestock': predicciones_payload.sobrestock,
        'pred_top': predicciones_payload.items[:5],
        'pred_fecha_generacion': predicciones_payload.fecha_generacion,
    }
    return render(request, 'dashboard.html', context)


@login_required
def lista_productos(request):
    productos_qs = Productos.objects.all().order_by('-id_producto')
    productos = list(productos_qs)
    metricas = _calcular_metricas(productos, decorar=True)
    marcas_registradas = (
        productos_qs
        .exclude(brand__isnull=True)
        .exclude(brand__exact='')
        .values('brand')
        .distinct()
        .count()
    )
    context = {
        'productos': productos,
        'is_admin': _user_is_admin(request.user),
        'total_productos': metricas['total'],
        'productos_disponibles': metricas['disponibles'],
        'productos_sin_stock': metricas['sin_stock'],
        'productos_en_oferta': metricas['en_oferta'],
        'marcas_registradas': marcas_registradas,
        'productos_inconsistentes': metricas['inconsistentes'],
    }
    return render(request, 'productos.html', context)


@login_required
@admin_required
def prediccion_productos(request):
    predicciones_payload = generar_predicciones()
    context = {
        'predicciones': predicciones_payload.items,
        'sugerencias_count': predicciones_payload.sugerencias,
        'sobrestock_count': predicciones_payload.sobrestock,
        'fecha_generacion': predicciones_payload.fecha_generacion,
    }
    return render(request, 'prediccion.html', context)


@login_required
@admin_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('productos')
    else:
        form = ProductoForm()
    return render(request, 'producto_form.html', {'form': form, 'accion': 'Agregar Producto'})


@login_required
@admin_required
def editar_producto(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'producto_form.html', {'form': form, 'accion': 'Editar Producto'})


@login_required
@admin_required
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('productos')
    return render(request, 'producto_confirm_delete.html', {'producto': producto})


@login_required
@admin_required
def informes(request):
    predicciones_payload = generar_predicciones()
    context = {
        'predicciones_resumen': {
            'sugerencias': predicciones_payload.sugerencias,
            'sobrestock': predicciones_payload.sobrestock,
            'total': len(predicciones_payload.items),
            'fecha_generacion': predicciones_payload.fecha_generacion,
        },
        'hay_sugerencias': predicciones_payload.sugerencias > 0,
        'hay_resumen_stock': len(predicciones_payload.items) > 0,
    }
    return render(request, 'informes.html', context)


@login_required
@admin_required
def usuarios(request):
    trabajadores = (
        User.objects
        .filter(is_active=True, is_staff=False, is_superuser=False)
        .order_by('username')
    )
    context = {'trabajadores': trabajadores}
    return render(request, 'usuarios.html', context)


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


@login_required
@admin_required
def exportar_reporte_compras(request):
    payload = generar_predicciones()
    filas = exportar_reporte_compras_csv(payload)

    fecha = payload.fecha_generacion.strftime('%Y%m%d_%H%M')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=reporte_compras_{fecha}.csv'

    writer = csv.writer(response)
    writer.writerows(filas)
    return response


@login_required
@admin_required
def exportar_reporte_stock(request):
    payload = generar_predicciones()
    filas = exportar_reporte_stock_csv(payload)

    fecha = payload.fecha_generacion.strftime('%Y%m%d_%H%M')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=resumen_stock_{fecha}.csv'

    writer = csv.writer(response)
    writer.writerows(filas)
    return response
