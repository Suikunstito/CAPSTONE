# SmartERP - Sistema Modular de Inventario Django

## 1. Visión General

**SmartERP** es un sistema Django con **arquitectura modular por dominios** para gestión integral de inventario, productos, ventas y usuarios. El proyecto ha sido **completamente refactorizado** desde una arquitectura monolítica hacia una estructura escalable y mantenible.

**Arquitectura actual:**
- ✅ **Modularidad por dominios**: 4 apps especializadas (users, catalog, inventory, sales)
- ✅ **Servicios de lógica de negocio**: Separación clara entre vistas y lógica
- ✅ **Templates organizados**: Herencia global con especialización por dominio
- ✅ **URLs modulares**: Routing distribuido con include()
- ❌ NO incluye APIs REST, pipelines de estáticos, ni frameworks JS

**Alcance funcional:**
- 🔐 Autenticación y gestión de usuarios
- 📦 Catálogo completo de productos (CRUD)
- 📊 Dashboard con estadísticas e inventario
- 💰 Estructura para gestión de ventas (extensible)

## 2. Arquitectura Modular por Dominios

### Árbol de Directorios SmartERP
```
appSmart/ (SmartERP)
├── manage.py                       # Punto de entrada Django
├── templates/                      # Templates globales (base.html)
├── inventario_web/                 # Configuración Django principal
│   ├── settings.py                 # INSTALLED_APPS modular
│   ├── urls.py                     # Router principal con include()
│   └── wsgi.py                     # WSGI config
├── users/                          # 🔐 DOMINIO: Autenticación
│   ├── views/auth.py               # CustomLoginView
│   ├── templates/users/            # login.html mejorado
│   └── urls.py                     # /login/, /logout/
├── catalog/                        # 📦 DOMINIO: Productos y Catálogo
│   ├── models/products.py          # Productos (managed=False)
│   ├── views/products.py           # CRUD productos
│   ├── forms/products.py           # ProductoForm
│   ├── templates/catalog/          # Templates productos
│   └── urls.py                     # /productos/*
├── inventory/                      # 📊 DOMINIO: Inventario y Dashboard
│   ├── models/movements.py         # StgProductosRaw + futuros movimientos
│   ├── views/dashboard.py          # Dashboard con estadísticas
│   ├── services/stock.py           # Lógica de stock y cálculos
│   ├── templates/inventory/        # dashboard.html con Chart.js
│   └── urls.py                     # / (dashboard raíz)
├── sales/                          # 💰 DOMINIO: Ventas (extensible)
│   ├── models/sales.py             # Ventas (managed=False)
│   ├── services/orders.py          # Lógica de transacciones
│   └── urls.py                     # Rutas futuras de ventas
└── .github/
    ├── README.md                   # Documentación arquitectura
    └── instructions/               # Guías técnicas modulares
```

### Mapeo de Rutas Modulares
| URL                          | App/Dominio | Vista              | Template                           | Función                   |
|------------------------------|-------------|--------------------|------------------------------------|---------------------------|
| `/`                          | inventory   | `dashboard`        | `inventory/dashboard.html`         | Panel estadísticas        |
| `/productos/`                | catalog     | `lista_productos`  | `catalog/productos.html`           | Lista productos           |
| `/productos/nuevo/`          | catalog     | `crear_producto`   | `catalog/producto_form.html`       | Crear producto            |
| `/productos/editar/<id>/`    | catalog     | `editar_producto`  | `catalog/producto_form.html`       | Editar producto           |
| `/productos/eliminar/<id>/`  | catalog     | `eliminar_producto`| `catalog/producto_confirm_delete.html` | Confirmar eliminación |
| `/login/`                    | users       | `CustomLoginView`  | `users/login.html`                 | Login mejorado            |
| `/logout/`                   | users       | `LogoutView`       | Redirect a login                   | Logout automático         |

## 3. Base de Datos (SQL Server)

### Configuración de Conexión
- **Motor**: `mssql` con ODBC Driver 17 para SQL Server
- **Servidor**: `DESKTOP-AU48ANV` (trusted connection)
- **Base**: `inventario`
- **Collation**: `Modern_Spanish_CI_AS` (obligatorio en todos los CharField)

### Modelos Distribuidos por Dominio
| Modelo          | Ubicación Modular | PK Personalizada | Relaciones                    | Estado     |
|-----------------|-------------------|------------------|-------------------------------|------------|
| `Productos`     | `catalog/models/products.py` | `id_producto`    | Referenciado por Ventas       | `managed=False` |
| `Ventas`        | `sales/models/sales.py`   | `id_venta`       | FK a `catalog.models.Productos`  | `managed=False` |
| `StgProductosRaw` | `inventory/models/movements.py` | (default) | Staging ETL + futuros movimientos | `managed=False` |

### Checklist de Seguridad Base de Datos
- ✅ Solo lectura/escritura ORM: usar `.objects.create()`, `.save()`, `.delete()`
- ✅ Consultas complejas: `.aggregate()`, `.annotate()` antes que raw SQL
- ❌ **NUNCA** ejecutar `makemigrations` o `migrate`
- ❌ **NUNCA** alterar esquema desde Django

## 4. Configuración de Entorno

### Variables de Entorno (.env)
```bash
DEBUG=True                    # Solo desarrollo
ALLOWED_HOSTS=*               # Lista separada por comas
```

### Requisitos del Sistema
- **Python**: Compatible con Django 5.2+
- **SQL Server**: Accesible desde red/local
- **ODBC Driver 17**: Instalado en Windows
- **python-dotenv**: Para carga de variables

### Dependencias Implícitas
```python
# Instaladas globalmente (sin requirements.txt actual)
django>=5.2
python-dotenv
mssql-driver  # Probable django-mssql o similar
```

## 4. Servicios de Lógica de Negocio (Nuevo)

### inventory/services/stock.py - Estadísticas y Stock
```python
from catalog.models.products import Productos

def get_stock_stats():
    """Estadísticas completas para dashboard"""
    return {
        'total_productos': Productos.objects.count(),
        'productos_con_stock': Productos.objects.filter(sin_stock=False).count(),
        'productos_sin_stock': Productos.objects.filter(sin_stock=True).count(),
        'productos_en_oferta': Productos.objects.filter(oferta=True).count(),
        'suma_precios': Productos.objects.aggregate(Sum('normal_price'))['normal_price__sum'],
    }

def calculate_inventory_value():
    """Valor total del inventario"""
    # Lógica centralizada reutilizable
```

### sales/services/orders.py - Lógica de Ventas
```python
from django.db import transaction
from catalog.models.products import Productos
from sales.models.sales import Ventas

@transaction.atomic
def register_sale(producto_id, cantidad, precio_unitario):
    """Registrar venta con validaciones transaccionales"""
    producto = Productos.objects.get(id_producto=producto_id)
    # Validaciones + creación de venta
    
def get_sales_summary(fecha_desde=None, fecha_hasta=None):
    """Resumen de ventas por período"""
    # Agregaciones de ventas por fechas
```

## 5. Patrones de Desarrollo Modulares

### Imports Entre Apps (Crítico)
```python
# ✅ CORRECTO: Imports explícitos entre dominios
from catalog.models.products import Productos          # Modelo productos
from inventory.services.stock import get_stock_stats   # Servicio inventario
from sales.services.orders import register_sale        # Servicio ventas

# ❌ INCORRECTO: Imports del app monolítico anterior
from productos.models import Productos  # Ya no existe
```

### Decoradores y Autenticación (Mantenido)
```python
@login_required                # Todas las vistas excepto login
LOGIN_REDIRECT_URL = '/productos/'  # Mantiene redirect original
LOGIN_URL = '/login/'
```

### Formularios Modulares
```python
# catalog/forms/products.py
from catalog.models.products import Productos

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['title', 'brand', 'normal_price', 'low_price', 'high_price',
                  'oferta', 'categoria1', 'categoria2', 'sin_stock', 'ahorro', 
                  'ahorro_percent', 'kilo']
        # Excluidos: datetime, page, total_venta, Atributos
```

### Uso de Servicios en Vistas
```python
# inventory/views/dashboard.py
from inventory.services.stock import get_stock_stats

@login_required
def dashboard(request):
    stats = get_stock_stats()  # Usa servicio en lugar de consultas directas
    context = {
        'total_productos': stats['total_productos'],
        'productos_con_stock': stats['productos_con_stock'],
        # ...
    }
    return render(request, 'inventory/dashboard.html', context)
```

## 6. Configuración Modular

### INSTALLED_APPS Actualizada
```python
# inventario_web/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps SmartERP - Arquitectura modular por dominio
    'users',           # Autenticación y roles
    'catalog',         # Productos y categorías  
    'inventory',       # Inventario y dashboard
    'sales',           # Ventas y transacciones
]
```

### URLs Principales con Include
```python
# inventario_web/urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),    # Dashboard raíz
    path('', include('catalog.urls')),      # /productos/*
    path('', include('users.urls')),        # /login/, /logout/
    path('', include('sales.urls')),        # Futuras rutas ventas
]
```

## 7. Comandos y Flujos Críticos

### Comandos Permitidos
```bash
python manage.py runserver           # Desarrollo local
python manage.py shell              # Consola Django
python manage.py check              # Validar configuración modular
```

### Comandos PROHIBIDOS
```bash
python manage.py makemigrations     # ❌ Modelos unmanaged
python manage.py migrate            # ❌ Esquema externo
python manage.py startapp           # ❌ Arquitectura ya establecida
```

### Flujo de Trabajo Modular: Nueva Funcionalidad
1. **Identificar dominio**: ¿users, catalog, inventory, sales?
2. **Definir vista** en `{app}/views/{module}.py` con `@login_required`
3. **Crear servicio** en `{app}/services/{module}.py` para lógica de negocio
4. **Agregar URL** en `{app}/urls.py`
5. **Crear template** en `{app}/templates/{app}/`
6. **Heredar** de `base.html` y usar `{% block content %}`
7. **Importar** servicios/modelos de otras apps si necesario

## 8. Guardrails Modulares (Muy Importante)

### Restricciones de Arquitectura Modular
- ❌ **No romper modularidad**: Evitar imports circulares entre apps
- ❌ **No retroceder a monolito**: No mover código de vuelta a `productos/`
- ❌ **No introducir frameworks**: DRF, React, Vue, Angular ni pipelines JS
- ❌ **No cambiar estructura**: Templates deben permanecer en `{app}/templates/{app}/`
- ❌ **No mezclar dominios**: Lógica de productos no va en `inventory/`

### Restricciones de Base de Datos (Mantenidas)
- ❌ **No cambiar PKs** (`id_producto`, `id_venta`) ni `managed=False`
- ❌ **No modificar collation** `Modern_Spanish_CI_AS`
- ❌ **No crear migraciones** ni alterar esquema desde Django
- ❌ **No ejecutar raw SQL** sin justificación documentada
- ❌ **No cambiar tipos** de campo (DecimalField, BooleanField)

### Restricciones de Servicios
- ❌ **No lógica en vistas**: Usar servicios para cálculos complejos
- ❌ **No duplicar lógica**: Reutilizar servicios entre vistas/apps
- ❌ **No servicios sin transacciones**: Usar `@transaction.atomic` para operaciones críticas

## 9. Extensiones Modulares Sugeridas (No Aplicar Automáticamente)

### Nuevas Apps por Dominio
- **`reports/`**: App para reportes y analytics con servicios especializados
- **`api/`**: API REST usando DRF, organizando endpoints por dominio
- **`notifications/`**: Sistema de notificaciones cross-app
- **`user_management/`**: Gestión avanzada de usuarios y permisos

### Mejoras de Servicios Actuales
```python
# inventory/services/stock.py - Extensiones
def get_low_stock_alert(threshold=5):
    """Productos con stock crítico"""
    # Implementar cuando se tengan movimientos reales
    
def calculate_stock_projection(days=30):
    """Proyección de stock futuro"""
    # Usar datos de ventas para predicciones

# sales/services/orders.py - Extensiones  
def get_monthly_sales_report():
    """Reporte mensual con gráficos"""
    # Integrar con servicios de inventory para cross-analytics
```

### Testing Modular No Invasivo
```python
# tests/ por cada app
# catalog/tests/test_products.py
def test_producto_form_valid_data(self):
    form = ProductoForm(data={'title': 'Test', 'brand': 'TestBrand'})
    self.assertTrue(form.is_valid())

# inventory/tests/test_services.py
@patch('catalog.models.products.Productos.objects')
def test_get_stock_stats(self, mock_productos):
    mock_productos.count.return_value = 100
    stats = get_stock_stats()
    self.assertEqual(stats['total_productos'], 100)
```

### Mejoras de Desarrollo Modular
```python
# requirements.txt actualizado para estructura modular
Django==5.2.x
python-dotenv==1.0.x
django-mssql==1.x.x
django-debug-toolbar==4.2.0  # Para debugging por app
django-extensions==3.2.x     # Para shell_plus y graph_models
```

---

## 10. Migración desde Arquitectura Monolítica

### ⚠️ Apps Deprecadas
- **`productos/`**: App monolítica DEPRECADA tras refactor modular
- **No usar imports** de `productos.models`, `productos.views`, etc.
- **Usar nuevas rutas** modulares en lugar de referencias antiguas

### ✅ Equivalencias Post-Migración
| Componente Anterior | Nueva Ubicación Modular | Notas |
|---------------------|-------------------------|--------|
| `productos.models.Productos` | `catalog.models.products.Productos` | Mismo modelo, nueva ubicación |
| `productos.views.dashboard` | `inventory.views.dashboard.dashboard` | Ahora usa servicios |
| `productos.views.lista_productos` | `catalog.views.products.lista_productos` | Template actualizado |
| `productos.forms.ProductoForm` | `catalog.forms.products.ProductoForm` | Imports actualizados |

### 🔄 Proceso de Verificación Post-Refactor
1. **Funcionamiento básico**: `python manage.py runserver`
2. **Login/auth**: Verificar `/login/` → redirect dashboard
3. **Dashboard**: Verificar estadísticas y Chart.js en `/`
4. **CRUD productos**: Verificar `/productos/` → crear/editar/eliminar
5. **Templates**: Verificar herencia correcta desde `base.html`
6. **Servicios**: Verificar que dashboard usa `get_stock_stats()`

---

**📋 Documentación modular actualizada**: Ver `.github/instructions/` para especificaciones por área:
- **`backend.md`** - Modelos distribuidos, vistas por app, servicios de lógica de negocio
- **`data-model.md`** - Esquema SQL Server, modelos por dominio, relaciones cruzadas
- **`views-templates.md`** - Templates organizados, herencia global, UI por app
- **`dev-environment.md`** - Setup con apps modulares, troubleshooting imports
- **`testing.md`** - Testing por app, mocks de servicios, pruebas de integración

**🚀 SmartERP Modular**: Arquitectura escalable, mantenible y preparada para crecimiento empresarial