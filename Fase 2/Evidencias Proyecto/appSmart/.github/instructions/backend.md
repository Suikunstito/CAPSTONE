# Backend Modular - SmartERP Django

## Modelos Distribuidos por Dominio

### Lista Completa de Modelos SmartERP

| Modelo          | Ubicación Modular | PK Personalizada | Campos Clave                                    | Estado         |
|-----------------|-------------------|------------------|-------------------------------------------------|----------------|
| `Productos`     | `catalog/models/products.py` | `id_producto`    | `title`, `brand`, `normal_price`, `sin_stock`   | `managed=False` |
| `Ventas`        | `sales/models/sales.py`   | `id_venta`       | `id_producto` (FK), `fecha`, `cantidad_vendida` | `managed=False` |
| `StgProductosRaw` | `inventory/models/movements.py` | `id` (default) | `title`, `brand`, `normal_price` (staging)      | `managed=False` |

### Convenciones de Modelos
- **PKs personalizadas**: Todos usan nombres específicos (`id_producto`, `id_venta`)
- **Collation obligatoria**: `db_collation='Modern_Spanish_CI_AS'` en CharField
- **Campos nullable**: `blank=True, null=True` en la mayoría de campos
- **Tipos decimales**: `DecimalField(max_digits=12, decimal_places=2)` para precios

### Ejemplo de Modelo Modular
```python
# catalog/models/products.py
from django.db import models

class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_collation='Modern_Spanish_CI_AS')
    normal_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sin_stock = models.BooleanField(blank=True, null=True)
    
    class Meta:
        managed = False  # ← CRÍTICO: nunca cambiar
        db_table = 'Productos'
    
    def __str__(self):
        return f"{self.title} - {self.brand or 'Sin marca'}"

# catalog/models/__init__.py - Exportación limpia
from .products import Productos
__all__ = ['Productos']
```

### Relaciones Cross-App
```python
# sales/models/sales.py
from django.db import models
from catalog.models.products import Productos  # Import entre apps

class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='id_producto')
    # ... resto de campos
    
    class Meta:
        managed = False
        db_table = 'Ventas'
```

## Vistas Modulares por Dominio

### Mapping Completo Modular URL → App → Vista → Template

| URL Pattern                     | App/Dominio | Vista              | Template                           | Método | Decorador       |
|---------------------------------|-------------|--------------------|------------------------------------|--------|-----------------|
| `/`                             | inventory   | `dashboard`        | `inventory/dashboard.html`         | GET    | `@login_required` |
| `/productos/`                   | catalog     | `lista_productos`  | `catalog/productos.html`           | GET    | `@login_required` |
| `/productos/nuevo/`             | catalog     | `crear_producto`   | `catalog/producto_form.html`       | GET/POST | `@login_required` |
| `/productos/editar/<int:id_producto>/` | catalog | `editar_producto` | `catalog/producto_form.html`    | GET/POST | `@login_required` |
| `/productos/eliminar/<int:id_producto>/` | catalog | `eliminar_producto` | `catalog/producto_confirm_delete.html` | GET/POST | `@login_required` |
| `/login/`                       | users       | `CustomLoginView`  | `users/login.html`                 | GET/POST | (público)       |
| `/logout/`                      | users       | `LogoutView`       | Redirect a login                   | POST   | (público)       |

## Servicios de Lógica de Negocio (Nuevo)

### inventory/services/stock.py - Estadísticas Centralizadas
```python
from django.db.models import Sum, Count
from catalog.models.products import Productos

def get_stock_stats():
    """
    Estadísticas completas de inventario para dashboard
    Centraliza lógica de negocio reutilizable
    """
    return {
        'total_productos': Productos.objects.count(),
        'productos_con_stock': Productos.objects.filter(sin_stock=False).count(),
        'productos_sin_stock': Productos.objects.filter(sin_stock=True).count(),
        'productos_en_oferta': Productos.objects.filter(oferta=True).count(),
        'suma_precios': Productos.objects.aggregate(Sum('normal_price'))['normal_price__sum'],
    }

def calculate_inventory_value():
    """Calcular valor total del inventario con promedio"""
    stats = Productos.objects.aggregate(
        total_value=Sum('normal_price'),
        count=Count('id_producto')
    )
    avg_price = stats['total_value'] / stats['count'] if stats['count'] else None
    return {
        'total_value': stats['total_value'] or 0,
        'average_price': avg_price,
        'products_count': stats['count'] or 0
    }
```

### sales/services/orders.py - Transacciones de Ventas
```python
from django.db import transaction
from catalog.models.products import Productos
from sales.models.sales import Ventas

@transaction.atomic
def register_sale(producto_id, cantidad, precio_unitario):
    """
    Registrar venta completa con validaciones
    Usa transacciones para consistencia
    """
    producto = Productos.objects.get(id_producto=producto_id)
    if cantidad <= 0 or precio_unitario <= 0:
        raise ValueError("Cantidad y precio deben ser positivos")
    
    total = cantidad * precio_unitario
    return Ventas.objects.create(
        id_producto=producto,
        fecha=timezone.now().date(),
        cantidad_vendida=cantidad,
        precio_unitario=precio_unitario,
        total_venta=total
    )
```

### Patrones de Vistas Modulares

#### Dashboard con Servicios
```python
# inventory/views/dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from inventory.services.stock import get_stock_stats

@login_required
def dashboard(request):
    """Dashboard usando servicios en lugar de consultas directas"""
    stats = get_stock_stats()  # Usa servicio centralizado
    
    context = {
        'total_productos': stats['total_productos'],
        'productos_con_stock': stats['productos_con_stock'],
        'productos_sin_stock': stats['productos_sin_stock'],
        'productos_en_oferta': stats['productos_en_oferta'],
        'promedio_precio': stats['suma_precios'],
    }
    return render(request, 'inventory/dashboard.html', context)
```

#### CRUD Modular con Imports Cross-App
```python
# catalog/views/products.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from catalog.models.products import Productos  # Modelo del mismo dominio
from catalog.forms.products import ProductoForm  # Form del mismo dominio

@login_required
def editar_producto(request, id_producto):
    """Editar producto con PK personalizada y form modular"""
    producto = get_object_or_404(Productos, id_producto=id_producto)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'catalog/producto_form.html', 
                  {'form': form, 'accion': 'Editar Producto'})
```

## URLs Modulares por Dominio

### inventario_web/urls.py - Router Principal
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Apps modulares con include()
    path('', include('inventory.urls')),    # Dashboard raíz
    path('', include('catalog.urls')),      # /productos/*
    path('', include('users.urls')),        # /login/, /logout/
    path('', include('sales.urls')),        # Futuras rutas ventas
]
```

### inventory/urls.py - Dashboard
```python
from django.urls import path
from inventory.views.dashboard import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),  # Ruta raíz "/"
]
```

### catalog/urls.py - CRUD Productos
```python
from django.urls import path
from catalog.views import products

urlpatterns = [
    path('productos/', products.lista_productos, name='productos'),
    path('productos/nuevo/', products.crear_producto, name='crear_producto'),
    path('productos/editar/<int:id_producto>/', products.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', products.eliminar_producto, name='eliminar_producto'),
]
```

### users/urls.py - Autenticación
```python
from django.urls import path
from django.contrib.auth import views as auth_views
from users.views.auth import CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
```

## Formularios Modulares

### catalog/forms/products.py - ProductoForm
```python
from django import forms
from catalog.models.products import Productos  # Import del mismo dominio

class ProductoForm(forms.ModelForm):
    """
    Formulario modular para productos
    Ubicado en el dominio catalog junto al modelo
    """
    class Meta:
        model = Productos
        fields = [
            'title',           # Título producto
            'brand',           # Marca
            'normal_price',    # Precio normal
            'low_price',       # Precio bajo
            'high_price',      # Precio alto
            'oferta',          # Boolean - en oferta
            'categoria1',      # Categoría primaria
            'categoria2',      # Categoría secundaria
            'sin_stock',       # Boolean - sin stock
            'ahorro',          # Decimal - ahorro calculado
            'ahorro_percent',  # Decimal - porcentaje ahorro
            'kilo'             # Float - peso/kilo
        ]
        # EXCLUIDOS: datetime, page, total_venta, Atributos (computados)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO(doc-sync): Widgets personalizados por dominio

# catalog/forms/__init__.py - Exportación limpia
from .products import ProductoForm
__all__ = ['ProductoForm']
```

### Validaciones Implícitas
- **DecimalField**: Validación automática de dígitos y decimales
- **BooleanField**: Acepta `True/False/None` (nullable)
- **CharField**: Max length según modelo + collation

## Consultas ORM Modulares

### Consultas con Imports Cross-App
```python
# inventory/services/stock.py
from catalog.models.products import Productos  # Import entre apps

# Consultas centralizadas en servicios
def get_stock_stats():
    return {
        'total_productos': Productos.objects.count(),
        'productos_con_stock': Productos.objects.filter(sin_stock=False).count(),
        'productos_en_oferta': Productos.objects.filter(oferta=True).count(),
    }
```

### Consultas de Lista y CRUD (Por Dominio)
```python
# catalog/views/products.py
from catalog.models.products import Productos

# Lista ordenada en dominio catalog
productos = Productos.objects.all().order_by('-id_producto')

# Búsqueda con PK personalizada mantenida
producto = get_object_or_404(Productos, id_producto=id_producto)

# Filtros específicos del catálogo
ofertas_activas = Productos.objects.filter(oferta=True, sin_stock=False)
```

### Consultas con Relaciones Cross-App
```python
# sales/services/orders.py
from catalog.models.products import Productos
from sales.models.sales import Ventas

# Ventas de un producto (relación entre dominios)
def get_product_sales(producto_id):
    ventas = Ventas.objects.filter(id_producto=producto_id)
    return ventas.aggregate(
        total_cantidad=Sum('cantidad_vendida'),
        total_ingresos=Sum('total_venta')
    )

# Productos más vendidos (cross-domain analytics)
def get_top_selling_products():
    # TODO(doc-sync): Implementar GROUP BY cross-app
    pass
```

### Transacciones Multi-Dominio
```python
# sales/services/orders.py
from django.db import transaction

@transaction.atomic
def complete_sale_with_inventory_update(producto_id, cantidad):
    """
    Venta completa con actualización de inventario
    Usa transacción para consistencia cross-domain
    """
    # 1. Crear venta en sales
    venta = register_sale(producto_id, cantidad, precio)
    
    # 2. Actualizar stock en inventory (futuro)
    # update_inventory_movement(producto_id, cantidad, 'out')
    
    return venta
```

## Guardrails Backend Modulares

### Restricciones de Arquitectura Modular
- ❌ **NUNCA** crear imports circulares entre apps (`catalog` ↔ `sales`)
- ❌ **NUNCA** poner lógica de negocio directamente en vistas (usar servicios)
- ❌ **NUNCA** mezclar dominios (lógica de productos en `inventory/`)
- ❌ **NUNCA** romper encapsulación (acceso directo a modelos de otras apps sin servicios)

### Restricciones de Modelos (Mantenidas)
- ❌ **NUNCA** cambiar `managed = False` a `managed = True`
- ❌ **NUNCA** ejecutar `makemigrations` o `migrate`
- ❌ **NUNCA** modificar nombres de PK (`id_producto`, `id_venta`)
- ❌ **NUNCA** alterar `db_collation='Modern_Spanish_CI_AS'`
- ❌ **NUNCA** cambiar tipos de campo (DecimalField → FloatField)

### Restricciones de Vistas Modulares
- ❌ **NUNCA** omitir `@login_required` (excepto login/público)
- ❌ **NUNCA** usar raw SQL sin documentar justificación
- ❌ **NUNCA** hacer consultas complejas en vistas (usar servicios)
- ❌ **NUNCA** duplicar lógica entre vistas de diferentes apps

### Restricciones de URLs Modulares
- ❌ **NUNCA** cambiar patrón `<int:id_producto>` por `<int:pk>`
- ❌ **NUNCA** crear URLs que rompan la modularidad por dominio
- ❌ **NUNCA** duplicar rutas entre apps sin `namespace`

### Restricciones de Servicios
- ❌ **NUNCA** crear servicios sin `@transaction.atomic` para operaciones críticas
- ❌ **NUNCA** duplicar lógica entre servicios de diferentes apps
- ❌ **NUNCA** acceder directamente a modelos desde servicios de otras apps sin interfaces claras

## Sugerencias Modulares (No Aplicar Automáticamente)

### Nuevas Apps por Dominio
```python
# reports/ - App de reportes cross-domain
def generate_inventory_sales_report():
    """Combina datos de inventory + sales para reportes"""
    from inventory.services.stock import get_stock_stats
    from sales.services.orders import get_sales_summary
    # Combinar datos de múltiples dominios

# api/ - API REST modular
# api/catalog/views.py
class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.all()
    # API específica del dominio catalog
```

### Mejoras de Servicios
```python
# inventory/services/stock.py - Extensiones
def get_stock_alerts(threshold=5):
    """Alertas de stock bajo por dominio"""
    from catalog.models.products import Productos
    return Productos.objects.filter(
        # TODO(doc-sync): Implementar con movimientos reales
        sin_stock=True
    )

# catalog/services/products.py - Nuevo servicio
def bulk_update_prices(price_adjustment):
    """Actualización masiva de precios"""
    # Lógica específica del dominio catalog
```

### Mejoras de Performance Modular
```python
# catalog/views/products.py - Paginación
from django.core.paginator import Paginator

def lista_productos(request):
    productos_list = Productos.objects.all().order_by('-id_producto')
    paginator = Paginator(productos_list, 25)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
    return render(request, 'catalog/productos.html', {'productos': productos})
```

### Mejoras de Validación Cross-App
```python
# catalog/forms/products.py - Validaciones avanzadas
from django.core.exceptions import ValidationError

class ProductoForm(forms.ModelForm):
    def clean_normal_price(self):
        price = self.cleaned_data.get('normal_price')
        if price and price <= 0:
            raise ValidationError('El precio debe ser mayor a 0.')
        return price
    
    def clean(self):
        cleaned_data = super().clean()
        # TODO(doc-sync): Validaciones cross-domain con servicios
        return cleaned_data
```

### Testing Modular
```python
# catalog/tests/test_services.py
class CatalogServicesTest(TestCase):
    def test_producto_creation_service(self):
        # Test específico del dominio catalog
        pass

# inventory/tests/test_services.py  
class InventoryServicesTest(TestCase):
    @patch('catalog.models.products.Productos.objects')
    def test_stock_stats_service(self, mock_productos):
        # Test del servicio usando mocks de otros dominios
        pass
```

---

**Guardrails para Copilot (bloque estándar):**
- No sugieras ejecutar `makemigrations` ni `migrate`.
- No propongas cambiar `managed=False` ni las PKs actuales.
- No introduzcas frameworks (DRF, React) ni pipelines de estáticos.
- No modifiques collation ni la conexión a SQL Server.
- No reestructures plantillas fuera de su ubicación actual.
- Si propones una mejora, ubícala en **"Sugerencias (no aplicar automáticamente)"**.