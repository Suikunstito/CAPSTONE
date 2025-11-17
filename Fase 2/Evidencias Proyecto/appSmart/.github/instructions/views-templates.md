# Vistas y Templates - Frontend Django

## Estructura Real de Plantillas

### Jerarquía de Templates
```
productos/templates/
├── base.html                    # Template base con CSS inline
├── dashboard.html               # Panel estadísticas + Chart.js  
├── productos.html               # Lista completa de productos
├── producto_form.html           # Crear/editar producto (reutilizado)
├── producto_confirm_delete.html # Confirmación eliminación
└── login.html                   # Login personalizado
```

### Herencia y Bloques
```django
<!-- base.html -->
<title>{% block title %}Inventario{% endblock %}</title>
<div class="content">{% block content %} {% endblock %}</div>

<!-- Ejemplo: dashboard.html -->
{% extends "base.html" %}
{% block title %}Inicio - Dashboard{% endblock %}
{% block content %}
    <h2>📊 Panel de control</h2>
    <!-- contenido específico -->
{% endblock %}
```

### CSS y Estilos en Línea
**Ubicación**: Todo el CSS está **inline** en `base.html` (líneas 6-58)
- Header azul (`#0078d7`) con navegación horizontal
- Cards de estadísticas con colores específicos (azul, verde, rojo, amarillo)
- Estilos de formularios, botones y enlaces
- **NO hay archivos CSS externos** ni pipelines de estáticos

## Estándares de UI/HTML

### Paleta de Colores Consistente
| Elemento              | Color     | Uso                           |
|-----------------------|-----------|-------------------------------|
| Header/Primary        | `#0078d7` | Cabecera, botones principales |
| Success/Stock         | `#28a745` | Productos con stock           |
| Danger/Sin Stock      | `#dc3545` | Productos sin stock           |
| Warning/Oferta        | `#ffc107` | Productos en oferta           |
| Background            | `#f9f9f9` | Fondo general                 |

### Estructura de Cards (Dashboard)
```html
<div style="background:#0078d7;color:white;padding:20px;border-radius:8px;flex:1;min-width:220px;">
    <h3>Total de Productos</h3>
    <p style="font-size: 24px;">{{ total_productos }}</p>
</div>
```

### Navegación Estándar
```html
<nav>
    {% if user.is_authenticated %}
    <span class="user">👋 {{ user.username }}</span>
    <a href="{% url 'dashboard' %}">Inicio</a>
    <a href="{% url 'productos' %}">Productos</a>
    <form action="{% url 'logout' %}" method="post" class="logout-form">
        {% csrf_token %}
        <button type="submit">Cerrar sesión</button>
    </form>
    {% endif %}
</nav>
```

## Patrones de Contexto por Vista

### Dashboard (dashboard.html)
**Variables de contexto enviadas:**
```python
context = {
    'total_productos': int,           # Conteo total
    'productos_con_stock': int,       # Sin stock=False  
    'productos_sin_stock': int,       # Sin stock=True
    'productos_en_oferta': int,       # oferta=True
    'promedio_precio': Decimal,       # Suma de normal_price
}
```

**Chart.js integrado:**
- CDN: `https://cdn.jsdelivr.net/npm/chart.js`
- Gráfico de dona con datos del contexto
- Canvas ID: `chartProductos`

### Lista de Productos (productos.html)
**Variables de contexto:**
```python
context = {
    'productos': QuerySet,  # Productos.objects.all().order_by('-id_producto')
}
```

**Estructura de tabla:**
| Columna       | Campo Modelo      | Formato                    |
|---------------|-------------------|----------------------------|
| ID            | `id_producto`     | Número simple              |
| Título        | `title`           | Texto completo             |
| Marca         | `brand`           | Texto o "N/A" si null      |
| Precio        | `normal_price`    | `${{ precio|floatformat:2 }}` |
| Stock         | `sin_stock`       | "Sí" / "No" (boolean)      |
| Oferta        | `oferta`          | "Sí" / "No" (boolean)      |

### Formularios (producto_form.html)
**Variables de contexto:**
```python
context = {
    'form': ProductoForm,      # Instancia del formulario
    'accion': str,             # "Agregar Producto" o "Editar Producto"
}
```

**Estructura del formulario:**
```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}  <!-- Renderizado automático Django -->
    <button type="submit">{{ accion }}</button>
    <a href="{% url 'productos' %}">Cancelar</a>
</form>
```

### Confirmación Eliminación (producto_confirm_delete.html)
**Variables de contexto:**
```python
context = {
    'producto': Productos,  # Instancia específica a eliminar
}
```

## Integración con JavaScript

### Chart.js en Dashboard
```html
<!-- Carga de librería -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Configuración del gráfico -->
<script>
document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('chartProductos').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Con Stock', 'Sin Stock', 'En Oferta'],
            datasets: [{
                data: [
                    {{ productos_con_stock }},
                    {{ productos_sin_stock }}, 
                    {{ productos_en_oferta }}
                ],
                backgroundColor: ['#28a745', '#dc3545', '#ffc107']
            }]
        }
    });
});
</script>
```

### Formularios con Django
- **CSRF Token**: `{% csrf_token %}` en todos los POST
- **Validación**: Automática vía `form.is_valid()`
- **Errores**: `{{ form.errors }}` o `{{ field.errors }}`

## Mensajes al Usuario

### Patrones Actuales
- **Sin sistema de mensajes flash** implementado
- Redirección directa post-éxito (`redirect('productos')`)
- Errores mostrados vía `form.errors` en template

### Estructura HTML de Mensajes (No implementada)
```html
<!-- Patrón sugerido para mensajes -->
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
    {% endfor %}
{% endif %}
```

## URLs y Navegación

### Mapa de Navegación Real
```
Inicio (/) 
├── Dashboard con estadísticas
├── Navegación → "Productos" (/productos/)
│   ├── Lista de productos
│   ├── Botón "Nuevo Producto" → (/productos/nuevo/)
│   ├── Links "Editar" → (/productos/editar/<id>/)
│   └── Links "Eliminar" → (/productos/eliminar/<id>/)
└── Logout → (/login/)
```

### Template Tags Utilizados
```django
{% url 'dashboard' %}           # URL reversa
{% csrf_token %}                # Protección CSRF
{% block title %}...{% endblock %} # Herencia de bloques
{% extends "base.html" %}       # Herencia de template
{{ variable|floatformat:2 }}    # Filtro para decimales
{% if user.is_authenticated %}  # Condicional de auth
```

## Guardrails de Templates

### Restricciones de Estructura
- ❌ **NUNCA** mover templates fuera de `productos/templates/`
- ❌ **NUNCA** introducir frameworks JS (React, Vue, Angular)
- ❌ **NUNCA** crear pipelines de build para CSS/JS
- ❌ **NUNCA** separar CSS inline sin planificación explícita

### Restricciones de Funcionalidad  
- ❌ **NUNCA** exponer datos sensibles en contexto sin validación
- ❌ **NUNCA** omitir `{% csrf_token %}` en formularios POST
- ❌ **NUNCA** hardcodear URLs en lugar de `{% url %}`
- ❌ **NUNCA** mezclar lógica de negocio en templates

### Restricciones de Estilo
- ❌ **NUNCA** cambiar paleta de colores sin documentar
- ❌ **NUNCA** alterar estructura de header/nav existente
- ❌ **NUNCA** introducir librerías CSS (Bootstrap, etc.) sin justificación

## Sugerencias (No Aplicar Automáticamente)

### Mejoras de UX
```html
<!-- Tabla responsiva para productos -->
<div style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #0078d7; color: white;">
                <th>ID</th><th>Título</th><th>Marca</th><th>Precio</th>
            </tr>
        </thead>
        <!-- ... filas de datos -->
    </table>
</div>
```

### Sistema de Mensajes Flash
```python
# En views.py
from django.contrib import messages

def crear_producto(request):
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado exitosamente.')
        return redirect('productos')
```

```html
<!-- En base.html, después del header -->
{% if messages %}
    <div style="padding: 10px;">
        {% for message in messages %}
            <div style="padding: 10px; margin: 5px 0; border-radius: 4px; 
                        background: {% if message.tags == 'success' %}#d4edda{% elif message.tags == 'error' %}#f8d7da{% endif %};">
                {{ message }}
            </div>
        {% endfor %}
    </div>
{% endif %}
```

### Componentes Reutilizables
```html
<!-- Snippet: card de estadística -->
{% comment %}
    Uso: {% include 'partials/stat_card.html' with title="Total" value=total_productos color="#0078d7" %}
{% endcomment %}
<div style="background:{{ color }};color:white;padding:20px;border-radius:8px;flex:1;min-width:220px;">
    <h3>{{ title }}</h3>
    <p style="font-size: 24px;">{{ value }}</p>
</div>
```

### Validación Frontend
```html
<!-- Validación HTML5 en formularios -->
<input type="number" name="normal_price" min="0" step="0.01" required>
<input type="text" name="title" maxlength="255" required>
```

---

**Guardrails para Copilot (bloque estándar):**
- No sugieras ejecutar `makemigrations` ni `migrate`.
- No propongas cambiar `managed=False` ni las PKs actuales.
- No introduzcas frameworks (DRF, React) ni pipelines de estáticos.
- No modifiques collation ni la conexión a SQL Server.
- No reestructures plantillas fuera de su ubicación actual.
- Si propones una mejora, ubícala en **"Sugerencias (no aplicar automáticamente)"**.