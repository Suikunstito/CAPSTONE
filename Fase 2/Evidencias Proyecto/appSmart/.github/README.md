# SmartERP - Sistema Modular de Inventario

## 🚀 Arquitectura Refactorizada

Este proyecto ha sido **completamente refactorizado** de una arquitectura monolítica a una **arquitectura modular por dominios**, transformando `appSmart` en un verdadero sistema **SmartERP**.

### 🏗️ Estructura Modular Final

```
appSmart/
├── inventario_web/              # Configuración Django principal
├── templates/                   # Templates globales (base.html)
├── users/                       # 🔐 Dominio: Autenticación
│   ├── views/auth.py           # Login personalizado
│   ├── templates/users/        # Templates de autenticación
│   └── urls.py                 # Rutas auth (/login/, /logout/)
├── catalog/                     # 📦 Dominio: Productos y Catálogo
│   ├── models/products.py      # Modelo Productos (managed=False)
│   ├── views/products.py       # CRUD productos
│   ├── forms/products.py       # ProductoForm
│   ├── templates/catalog/      # Templates productos
│   └── urls.py                 # Rutas productos (/productos/*)
├── inventory/                   # 📊 Dominio: Inventario y Dashboard
│   ├── models/movements.py     # StgProductosRaw + futuros movimientos
│   ├── views/dashboard.py      # Dashboard con estadísticas
│   ├── services/stock.py       # Lógica de negocio de stock
│   ├── templates/inventory/    # Template dashboard
│   └── urls.py                 # Ruta raíz (/)
├── sales/                      # 💰 Dominio: Ventas (futuro)
│   ├── models/sales.py         # Modelo Ventas (managed=False)
│   ├── services/orders.py      # Lógica de transacciones
│   └── urls.py                 # Rutas ventas (futuro)
└── .github/
    ├── README.md               # Este archivo
    └── instructions/           # Documentación técnica modular
```

## 🔄 Comparación: Antes vs Después

### ❌ Arquitectura Anterior (Monolítica)
```
productos/
├── models.py        # TODOS los modelos mezclados
├── views.py         # TODAS las vistas en un archivo
├── urls.py          # TODAS las rutas mezcladas
└── templates/       # Templates mezclados sin organización
```

### ✅ Arquitectura Actual (Modular por Dominio)
```
users/         → Autenticación separada
catalog/       → Productos y catálogo independiente
inventory/     → Dashboard y lógica de inventario
sales/         → Ventas y transacciones (escalable)
```

## 🎯 Beneficios del Refactor

### 📈 Escalabilidad
- **Equipos independientes**: Cada dominio puede desarrollarse por equipos separados
- **Deployments modulares**: Posibilidad de deployar apps por separado
- **Testing aislado**: Tests específicos por dominio

### 🧹 Mantenibilidad
- **Separación de responsabilidades**: Cada app tiene un propósito claro
- **Código más limpio**: Lógica de negocio en servicios reutilizables
- **Imports explícitos**: Dependencias claras entre dominios

### 🔧 Extensibilidad
- **Nuevos dominios**: Fácil agregar `reports/`, `analytics/`, `users_management/`
- **APIs futuras**: Estructura preparada para REST APIs por dominio
- **Microservicios**: Base para eventual migración a microservicios

## 🛠️ Servicios de Lógica de Negocio

### inventory/services/stock.py
```python
def get_stock_stats():
    """Estadísticas para dashboard"""
    return {
        'total_productos': ...,
        'productos_con_stock': ...,
        'productos_en_oferta': ...,
    }

def calculate_inventory_value():
    """Valor total del inventario"""
    # Lógica centralizada reutilizable
```

### sales/services/orders.py
```python
def register_sale(producto_id, cantidad, precio):
    """Registrar venta con validaciones y transacciones"""
    # TODO(doc-sync): Implementar integración con inventory

def get_sales_summary(fecha_desde, fecha_hasta):
    """Resumen de ventas por período"""
    # Lógica de reportes reutilizable
```

## 🔗 Compatibilidad y URLs

### URLs Mantenidas (Sin Romper Funcionalidad)
| URL Original | Nueva Ubicación | Estado |
|-------------|-----------------|---------|
| `/` | `inventory/urls.py` → dashboard | ✅ Funcional |
| `/productos/` | `catalog/urls.py` → CRUD | ✅ Funcional |
| `/login/` | `users/urls.py` → auth | ✅ Funcional |

### Templates Reubicados
| Template Original | Nueva Ubicación | Cambios |
|------------------|-----------------|---------|
| `dashboard.html` | `inventory/templates/inventory/` | Título actualizado |
| `productos.html` | `catalog/templates/catalog/` | Columna stock mejorada |
| `login.html` | `users/templates/users/` | Diseño mejorado |
| `base.html` | `templates/` (global) | Título "SmartERP" |

## 🔄 Migración Realizada

### Modelos Redistribuidos
- `Productos` → `catalog/models/products.py`
- `Ventas` → `sales/models/sales.py`
- `StgProductosRaw` → `inventory/models/movements.py`

### Vistas Separadas por Dominio
- Dashboard + estadísticas → `inventory/views/dashboard.py`
- CRUD productos → `catalog/views/products.py`
- Login personalizado → `users/views/auth.py`

### Formularios Modularizados
- `ProductoForm` → `catalog/forms/products.py`

## ⚙️ Configuración Actualizada

### INSTALLED_APPS (inventario_web/settings.py)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps SmartERP - Arquitectura modular
    'users',           # Autenticación
    'catalog',         # Productos
    'inventory',       # Dashboard e inventario
    'sales',           # Ventas
]
```

### URLs Principales (inventario_web/urls.py)
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),    # Dashboard
    path('', include('catalog.urls')),      # Productos
    path('', include('users.urls')),        # Auth
    path('', include('sales.urls')),        # Ventas (futuro)
]
```

## 🚨 Guardrails Mantenidos

### Base de Datos SQL Server
- ✅ **managed=False** preservado en todos los modelos
- ✅ **PKs personalizadas** mantenidas (`id_producto`, `id_venta`)
- ✅ **Collation** `Modern_Spanish_CI_AS` preservada
- ✅ **NO migraciones** ejecutadas durante refactor

### Funcionalidad Original
- ✅ Login/logout funcionando
- ✅ Dashboard con Chart.js intacto
- ✅ CRUD productos completo
- ✅ Mismas validaciones y formularios

## 🧪 Verificación Post-Refactor

### Comandos de Prueba
```bash
# Verificar estructura
python manage.py check

# Probar funcionalidad
python manage.py runserver
# Navegar: http://127.0.0.1:8000/
```

### Checklist Funcional
- [ ] Login funciona → redirect a dashboard
- [ ] Dashboard muestra estadísticas + gráfico
- [ ] Lista productos carga correctamente
- [ ] Crear producto funciona
- [ ] Editar producto funciona
- [ ] Eliminar producto funciona
- [ ] Logout redirect a login

## 📚 Documentación Técnica

Ver `.github/instructions/` para guías detalladas:

- **`backend.md`** - Modelos, vistas, URLs y servicios por app
- **`data-model.md`** - Esquema SQL Server y convenciones
- **`views-templates.md`** - Templates, herencia y patrones UI
- **`dev-environment.md`** - Setup local y troubleshooting
- **`testing.md`** - Testing no invasivo para modelos unmanaged

## 🎯 Próximos Pasos Sugeridos

### Funcionalidad Inmediata
1. **Testing**: Implementar tests unitarios por app
2. **Logging**: Configurar logs por dominio
3. **Validaciones**: Mejorar validaciones en formularios

### Expansión Modular
1. **reports/**: App para reportes y analytics
2. **api/**: API REST usando DRF (futuro)
3. **notifications/**: Sistema de notificaciones
4. **users_management/**: Gestión avanzada de usuarios

### Optimizaciones
1. **Servicios avanzados**: Implementar cálculo real de stock
2. **Cache**: Redis para estadísticas del dashboard
3. **Queue**: Celery para procesos ETL de StgProductosRaw

---

**⚡ SmartERP - Inventario modular y escalable**
*Refactorizado con arquitectura por dominios para crecimiento sostenible*
