# CAPSTONE - Sistema de Inventario Django

## 1. Arquitectura del Proyecto

**Inventario Web** es un sistema Django monolítico para gestión de inventario con predicciones ML integradas, conectado a SQL Server y organizado en fases de desarrollo académico.

### Estructura del Proyecto
```
CAPSTONE/
├── manage.py                       # Entry point Django
├── requirements.txt                # Dependencies con pandas/numpy para ML
├── inventario_web/                 # Configuración Django principal
│   ├── settings.py                 # Config SQL Server con trusted connection
│   └── urls.py                     # Router principal + auth routes
├── productos/                      # App principal monolítica
│   ├── models.py                   # Productos, Ventas, StgProductosRaw
│   ├── views.py                    # Todas las vistas + decoradores admin
│   ├── predicciones.py             # Sistema ML para recomendaciones compra
│   ├── forms.py                    # ProductoForm con validaciones
│   └── templates/                  # Templates sin subdirectorio
├── Fase 1/ & Fase 2/               # Evidencias académicas (no tocar)
└── .github/copilot-instructions.md # Este archivo
```

### Routing y URLs Principal
| URL | Vista | Template | Permisos |
|-----|-------|----------|----------|
| `/` | `productos.views.home` | `home.html` | `@login_required` |
| `/dashboard/` | `productos.views.dashboard` | `dashboard.html` | `@admin_required` |
| `/productos/` | `productos.views.lista_productos` | `productos.html` | `@login_required` |
| `/productos/nuevo/` | `productos.views.crear_producto` | `producto_form.html` | `@admin_required` |
| `/predicciones/` | `productos.views.prediccion_productos` | `prediccion.html` | `@admin_required` |
| `/informes/` | `productos.views.informes` | `informes.html` | `@admin_required` |

## 2. Base de Datos SQL Server

### Configuración Crítica
- **Servidor**: `AOANBC02CW0729\SQLEXPRESS` (trusted connection)
- **Base**: `inventario`
- **Driver**: ODBC Driver 17 for SQL Server
- **Collation**: `Modern_Spanish_CI_AS` (OBLIGATORIO en todos los CharField)

### Modelos (todos `managed=False`)
```python
# productos/models.py - NO ejecutar migraciones
class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)  # PK personalizada
    title = models.CharField(max_length=255, db_collation='Modern_Spanish_CI_AS')
    normal_price = models.DecimalField(max_digits=12, decimal_places=2)
    # ... otros campos con db_collation requerido
    
    class Meta:
        managed = False  # NO permitir migraciones Django
        db_table = 'Productos'
```

**⚠️ CRÍTICO**: Nunca ejecutar `makemigrations` o `migrate` - esquema controlado externamente.

## 3. Sistema de Predicciones ML

### Motor de Recomendaciones (`productos/predicciones.py`)
```python
# Dataclasses para predicciones estructuradas
@dataclass
class PredictionItem:
    producto: Productos
    promedio_mensual: float
    tendencia: float
    volatilidad: float
    probabilidad: float
    accion: str  # 'comprar', 'mantener', 'reducir'
    cantidad_sugerida: int

def generar_predicciones() -> PredictionPayload:
    # Algoritmo ML simple para recomendaciones de compra
    # Analiza histórico ventas + métricas stock
```

### Integración con Vistas
```python
# productos/views.py
@login_required
@admin_required
def prediccion_productos(request):
    predicciones = generar_predicciones()  # ML engine
    return render(request, 'prediccion.html', {
        'predicciones': predicciones,
        'fecha': predicciones.fecha_generacion
    })
```

## 4. Sistema de Autenticación y Permisos

### Decoradores Personalizados
```python
# productos/views.py
def _user_is_admin(user):
    return user.is_superuser or user.is_staff

@admin_required  # Decorador personalizado
def dashboard(request):
    # Solo admins acceden a dashboard y configuración
```

### Flujo de Login
- **Login**: `inventario_web/urls.py` → `productos.views.CustomLoginView`
- **Template**: `productos/templates/login.html`
- **Redirect**: `LOGIN_REDIRECT_URL = '/'` → home.html
- **Logout**: Django built-in → redirect a login

## 5. Patrones de Desarrollo Críticos

### Análisis de Productos (Core Business Logic)
```python
# productos/views.py - Lógica central reutilizada
def _analizar_producto(producto):
    """Determina estado del producto: disponible, en oferta, inconsistente"""
    tiene_precio = any(_valor_positivo(valor) for valor in 
                      (producto.normal_price, producto.low_price, producto.high_price))
    oferta_activa = bool(producto.oferta) or any(_valor_positivo(valor) 
                      for valor in (producto.ahorro, producto.ahorro_percent))
    inconsistente = bool(producto.sin_stock) and tiene_precio
    return tiene_precio, oferta_activa, inconsistente

def _calcular_metricas(productos, decorar=False):
    """Métricas agregadas para dashboard - usar siempre esta función"""
```

### Templates y Herencia
```html
<!-- productos/templates/base.html - Template base global -->
<!-- Todos los templates heredan con {% extends "base.html" %} -->
<!-- Chart.js integrado para dashboard estadísticas -->
<!-- Bootstrap 5 para UI responsivo -->
```

### Formularios con Validación
```python
# productos/forms.py
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['title', 'brand', 'normal_price', 'low_price', 'high_price',
                  'oferta', 'categoria1', 'categoria2', 'sin_stock'] 
        # Excluir: datetime, page, total_venta, Atributos (auto-populados)
```

## 6. Dependencias y Entorno

### Paquetes Críticos (`requirements.txt`)
```
Django==5.2.7
mssql-django==1.6          # SQL Server adapter
pyodbc==5.2.0             # ODBC driver interface  
pandas==2.3.3             # Data analysis para predicciones
numpy==2.3.4              # Cálculos ML
python-dateutil==2.9.0.post0  # Date handling
```

### Variables de Entorno (`.env` opcional)
```bash
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=inventario
DB_HOST=AOANBC02CW0729\\SQLEXPRESS
```

## 7. Comandos Permitidos/Prohibidos

### ✅ Comandos Seguros
```bash
python manage.py runserver           # Desarrollo local
python manage.py shell              # Django shell para testing
python manage.py check              # Validar configuración
python manage.py collectstatic      # Deploy assets
```

### ❌ Comandos PROHIBIDOS
```bash
python manage.py makemigrations     # Esquema SQL Server externo
python manage.py migrate            # NO tocar base de datos
python manage.py startapp           # Arquitectura monolítica establecida
```

## 8. Contexto Académico (Capstone Project)

### Estructura de Fases
- **`Fase 1/`**: Evidencias iniciales de análisis y diseño
- **`Fase 2/`**: Evidencias de implementación y testing
- **`Fase 2/Evidencias Proyecto/appSmart/`**: Prototipo modular futuro (no activo)

### Enfoque del Proyecto
- Sistema real de inventario con ML integrado
- Demostración de arquitectura Django escalable
- Integración con bases de datos empresariales (SQL Server)
- Implementación de algoritmos predictivos para negocio

**⚠️ Importante**: Este es el sistema ACTUAL en funcionamiento. Existe documentación de un sistema modular futuro en `Fase 2/appSmart/` que NO refleja la implementación actual.