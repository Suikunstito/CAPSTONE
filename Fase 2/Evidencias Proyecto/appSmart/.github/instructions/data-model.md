# Modelo de Datos - SQL Server

## Esquema Lógico Actual

### Tablas Principales del Sistema

| Tabla           | PK               | Descripción                           | Estado Django   |
|-----------------|------------------|---------------------------------------|-----------------|
| `Productos`     | `id_producto`    | Inventario principal con precios      | `managed=False` |
| `Ventas`        | `id_venta`       | Registro de transacciones de venta    | `managed=False` |
| `StgProductosRaw` | `id` (default) | Staging para ETL (datos sin procesar) | `managed=False` |

### Relaciones y Claves Foráneas

```
Productos (1) ←→ (N) Ventas
    id_producto ←→ id_producto (FK)
    
StgProductosRaw → [ETL Process] → Productos
    (staging)                     (production)
```

### Estructura Detallada por Tabla

#### Tabla: Productos
| Campo           | Tipo SQL           | Django Type          | Restricciones           | Descripción            |
|-----------------|--------------------|----------------------|-------------------------|------------------------|
| `id_producto`   | `INT IDENTITY(1,1)` | `AutoField(primary_key=True)` | PK, NOT NULL   | Identificador único    |
| `title`         | `NVARCHAR(255)`    | `CharField(max_length=255)` | Collation required | Nombre del producto    |
| `brand`         | `NVARCHAR(100)`    | `CharField(max_length=100)` | Nullable, Collation | Marca                  |
| `normal_price`  | `DECIMAL(12,2)`    | `DecimalField(12,2)` | Nullable                | Precio regular         |
| `low_price`     | `DECIMAL(12,2)`    | `DecimalField(12,2)` | Nullable                | Precio mínimo          |
| `high_price`    | `DECIMAL(12,2)`    | `DecimalField(12,2)` | Nullable                | Precio máximo          |
| `oferta`        | `BIT`              | `BooleanField`       | Nullable                | Si está en oferta      |
| `sin_stock`     | `BIT`              | `BooleanField`       | Nullable                | Si no tiene inventario |
| `datetime`      | `NVARCHAR(50)`     | `CharField(max_length=50)` | Nullable, Collation | Timestamp de registro  |
| `Atributos`     | `NVARCHAR(100)`    | `CharField(max_length=100)` | Nullable, Collation | Atributos adicionales  |

#### Tabla: Ventas
| Campo            | Tipo SQL           | Django Type          | Restricciones           | Descripción            |
|------------------|--------------------|----------------------|-------------------------|------------------------|
| `id_venta`       | `INT IDENTITY(1,1)` | `AutoField(primary_key=True)` | PK, NOT NULL   | Identificador único    |
| `id_producto`    | `INT`              | `ForeignKey(Productos)` | FK, NOT NULL         | Referencia a producto  |
| `fecha`          | `DATE`             | `DateField`          | NOT NULL                | Fecha de venta         |
| `cantidad_vendida` | `INT`            | `IntegerField`       | NOT NULL                | Unidades vendidas      |
| `precio_unitario` | `DECIMAL(12,2)`   | `DecimalField(12,2)` | NOT NULL                | Precio por unidad      |
| `total_venta`    | `DECIMAL(23,2)`    | `DecimalField(23,2)` | Nullable, Computed      | Total calculado        |

## Convenciones SQL Server

### Collation Obligatoria
**Todas las columnas string** deben usar:
```sql
COLLATE Modern_Spanish_CI_AS
```

En Django:
```python
title = models.CharField(max_length=255, db_collation='Modern_Spanish_CI_AS')
```

### Conexión y Configuración
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'inventario',
        'HOST': 'DESKTOP-AU48ANV',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
        },
    }
}
```

### Tipos de Datos y Precisión
| Propósito         | SQL Server Type    | Django Equivalent           | Notas                    |
|-------------------|--------------------|-----------------------------|--------------------------| 
| Precios/Dinero    | `DECIMAL(12,2)`    | `DecimalField(12,2)`        | 12 dígitos, 2 decimales  |
| Porcentajes       | `DECIMAL(12,3)`    | `DecimalField(12,3)`        | 3 decimales para %       |
| Booleanos         | `BIT`              | `BooleanField(null=True)`   | Nullable en BD           |
| Fechas            | `DATE`             | `DateField`                 | Solo fecha, sin hora     |
| Texto corto       | `NVARCHAR(n)`      | `CharField(max_length=n)`   | Con collation            |
| Peso/Medidas      | `FLOAT`            | `FloatField`                | Precisión variable       |

### Timezone y Fechas
- **SQL Server**: `UTC` o servidor local (verificar configuración)
- **Django**: `USE_TZ = True`, `TIME_ZONE = 'UTC'`
- **Campos datetime**: Usar formato `YYYY-MM-DD HH:MM:SS`

## Checklists

### Antes de Consultar Datos
- [ ] Verificar conexión ODBC activa
- [ ] Confirmar permisos de lectura en tabla
- [ ] Validar que tabla existe en esquema `inventario`
- [ ] Comprobar que filtros no retornen conjuntos masivos

### Al Escribir Datos
- [ ] Usar transacciones para operaciones múltiples
- [ ] Validar tipos de datos antes de `.save()`
- [ ] Verificar permisos de escritura
- [ ] No alterar campos computados (`total_venta`, `datetime`)
- [ ] Respetar restricciones de FK (productos existentes)

### Ejemplo de Transacción Segura
```python
from django.db import transaction

@transaction.atomic
def crear_venta_completa(producto_id, cantidad, precio_unitario):
    # Verificar producto existe
    producto = Productos.objects.get(id_producto=producto_id)
    
    # Calcular total
    total = cantidad * precio_unitario
    
    # Crear venta
    venta = Ventas.objects.create(
        id_producto=producto,
        fecha=datetime.date.today(),
        cantidad_vendida=cantidad,
        precio_unitario=precio_unitario,
        total_venta=total
    )
    
    return venta
```

## Guardrails de Datos

### Restricciones Críticas
- ❌ **NUNCA** ejecutar `makemigrations` o `migrate`
- ❌ **NUNCA** cambiar `managed = False` en modelos
- ❌ **NUNCA** alterar PKs personalizadas (`id_producto` → `id`)
- ❌ **NUNCA** modificar collation desde Django
- ❌ **NUNCA** crear/eliminar tablas desde Django ORM

### Restricciones de Esquema
- ❌ **NUNCA** renombrar columnas sin coordinación con DBA
- ❌ **NUNCA** cambiar tipos de datos (DECIMAL → FLOAT)
- ❌ **NUNCA** eliminar restricciones de FK existentes
- ❌ **NUNCA** alterar longitudes de VARCHAR sin validación

### Consultas Permitidas/Prohibidas
```python
# ✅ PERMITIDO - Consultas ORM de lectura
productos = Productos.objects.filter(sin_stock=False)
total = Productos.objects.count()

# ✅ PERMITIDO - Escritura ORM controlada  
producto.title = "Nuevo Nombre"
producto.save()

# ❌ PROHIBIDO - Raw SQL de estructura
cursor.execute("ALTER TABLE Productos ADD COLUMN nuevo_campo INT")

# ⚠️  CUIDADO - Raw SQL solo con justificación documentada
cursor.execute("SELECT * FROM Productos WHERE title LIKE %s", [pattern])
```

## Sugerencias (No Aplicar Automáticamente)

### Optimizaciones de Consultas
```python
# Índices sugeridos (implementar en SQL Server, no Django)
"""
CREATE INDEX IX_Productos_SinStock ON Productos(sin_stock) WHERE sin_stock = 0;
CREATE INDEX IX_Productos_Oferta ON Productos(oferta) WHERE oferta = 1;
CREATE INDEX IX_Ventas_Fecha ON Ventas(fecha);
"""

# Select related para FKs
ventas_con_producto = Ventas.objects.select_related('id_producto').all()
```

### Vistas SQL para Reportes
```sql
-- Vista sugerida: resumen productos
CREATE VIEW vw_productos_resumen AS
SELECT 
    p.id_producto,
    p.title,
    p.brand,
    p.normal_price,
    COALESCE(SUM(v.cantidad_vendida), 0) as total_vendido,
    COALESCE(SUM(v.total_venta), 0) as ingresos_totales
FROM Productos p
LEFT JOIN Ventas v ON p.id_producto = v.id_producto
GROUP BY p.id_producto, p.title, p.brand, p.normal_price;
```

### Backup y Recovery
- **Backup diario**: Programar respaldo automático de BD `inventario`
- **Log de transacciones**: Mantener logs para auditoría de cambios
- **Punto de restauración**: Antes de cambios masivos de datos

### Monitoreo de Performance
```python
# Logging de consultas lentas (settings.py)
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_sql.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['file'],
        }
    }
}
```

---

**Guardrails para Copilot (bloque estándar):**
- No sugieras ejecutar `makemigrations` ni `migrate`.
- No propongas cambiar `managed=False` ni las PKs actuales.
- No introduzcas frameworks (DRF, React) ni pipelines de estáticos.
- No modifiques collation ni la conexión a SQL Server.
- No reestructures plantillas fuera de su ubicación actual.
- Si propones una mejora, ubícala en **"Sugerencias (no aplicar automáticamente)"**.