# Testing - Pruebas No Invasivas

## Enfoque de Pruebas Compatible con Modelos Unmanaged

### Filosofía de Testing
- **Sin tocar el esquema**: Modelos `managed=False` prohíben crear/eliminar tablas de prueba
- **Sin fixtures de BD**: No se pueden cargar datos en tablas controladas externamente
- **Testing de lógica**: Enfocar en vistas, formularios, contextos y validaciones
- **Testing de integración**: Verificar conectividad y consultas de solo lectura

### Tipos de Pruebas Permitidas
| Tipo                  | Alcance                           | Seguridad      | Ejemplos                        |
|-----------------------|-----------------------------------|----------------|---------------------------------|
| **Vistas (GET)**      | Status codes, contexto, templates | ✅ Seguro       | Dashboard, lista productos      |
| **Formularios**       | Validación, campos, errores       | ✅ Seguro       | ProductoForm                    |
| **URLs**              | Resolución, parámetros, redirect  | ✅ Seguro       | Patrones de URL                 |
| **Consultas Read-Only** | ORM sin modificar datos         | ⚠️ Cuidadoso    | `.count()`, `.filter()`         |
| **Modelos (lógica)**  | Métodos, propiedades             | ✅ Seguro       | `__str__`, custom methods       |

### Tipos de Pruebas PROHIBIDAS
| Tipo                  | Problema                          | Alternativa                     |
|-----------------------|-----------------------------------|---------------------------------|
| **Crear instancias**  | `managed=False` + BD externa      | Mocks o datos existentes        |
| **Fixtures**          | No se pueden cargar en tablas     | Stubs con datos ficticios       |
| **Transacciones**     | Rollback no funciona con unmanaged | Testing en BD separada         |
| **Migraciones test**  | Crear tablas temporales prohibido | N/A para este proyecto          |

## Configuración de Testing

### Settings de Pruebas
```python
# tests_settings.py (archivo separado sugerido)
from .settings import *

# Base de datos de testing (separada)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # BD en memoria para tests que no usan modelos unmanaged
    }
}

# Deshabilitar migraciones
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Solo para testing
DEBUG = False
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Más rápido para tests
]
```

### Comando de Ejecución
```cmd
# Ejecutar con configuración separada
python manage.py test --settings=inventario_web.tests_settings

# O configurar en pytest.ini
python -m pytest
```

## Pruebas de Vistas (Status Codes y Contexto)

### Dashboard - Testing de Contexto
```python
# tests/test_views.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    @patch('productos.models.Productos.objects')
    def test_dashboard_context_structure(self, mock_productos):
        """Verificar que el dashboard envía las variables correctas"""
        # Mock de consultas ORM
        mock_productos.count.return_value = 100
        mock_productos.filter.return_value.count.side_effect = [80, 20, 15]
        mock_productos.aggregate.return_value = {'normal_price__sum': 5000.00}
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Panel de control')
        
        # Verificar contexto
        context = response.context
        self.assertIn('total_productos', context)
        self.assertIn('productos_con_stock', context)
        self.assertIn('productos_sin_stock', context)
        self.assertIn('productos_en_oferta', context)
        self.assertEqual(context['total_productos'], 100)

    def test_dashboard_requires_login(self):
        """Verificar que dashboard requiere autenticación"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/')
```

### Lista de Productos - Testing de Template
```python
class ProductosListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass')
    
    @patch('productos.models.Productos.objects')
    def test_productos_list_template_and_context(self, mock_productos):
        """Verificar template y contexto de lista de productos"""
        # Mock queryset
        mock_queryset = MagicMock()
        mock_queryset.all.return_value.order_by.return_value = []
        mock_productos.all.return_value.order_by.return_value = mock_queryset
        
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('productos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos.html')
        self.assertIn('productos', response.context)
```

## Pruebas de Formularios

### ProductoForm - Validación
```python
# tests/test_forms.py
from django.test import TestCase
from productos.forms import ProductoForm
from decimal import Decimal

class ProductoFormTest(TestCase):
    def test_producto_form_valid_data(self):
        """Prueba con datos válidos"""
        form_data = {
            'title': 'Producto Test',
            'brand': 'Marca Test',
            'normal_price': Decimal('99.99'),
            'low_price': Decimal('89.99'),
            'high_price': Decimal('109.99'),
            'oferta': True,
            'sin_stock': False,
            'kilo': 1.5
        }
        form = ProductoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_producto_form_missing_required_fields(self):
        """Prueba campos requeridos faltantes"""
        form_data = {}
        form = ProductoForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Verificar errores específicos sin depender de BD
    
    def test_producto_form_decimal_precision(self):
        """Verificar validación de precisión decimal"""
        form_data = {
            'title': 'Test',
            'normal_price': Decimal('999999999999.999'),  # Excede max_digits
        }
        form = ProductoForm(data=form_data)
        # Validar comportamiento sin tocar BD
        self.assertIn('normal_price', form.errors if not form.is_valid() else {})
```

## Pruebas de URLs

### Resolución y Parámetros
```python
# tests/test_urls.py
from django.test import TestCase
from django.urls import reverse, resolve
from productos import views

class URLsTest(TestCase):
    def test_dashboard_url_resolves(self):
        """Verificar que URLs se resuelven correctamente"""
        url = reverse('dashboard')
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, views.dashboard)
    
    def test_productos_crud_urls(self):
        """Verificar URLs de CRUD de productos"""
        urls_map = {
            'productos': '/productos/',
            'crear_producto': '/productos/nuevo/',
        }
        
        for name, expected_path in urls_map.items():
            url = reverse(name)
            self.assertEqual(url, expected_path)
    
    def test_producto_detail_urls_with_params(self):
        """Verificar URLs con parámetros"""
        url = reverse('editar_producto', kwargs={'id_producto': 123})
        self.assertEqual(url, '/productos/editar/123/')
        
        url = reverse('eliminar_producto', kwargs={'id_producto': 456})
        self.assertEqual(url, '/productos/eliminar/456/')
```

## Pruebas de Consultas Read-Only (Cuidadosas)

### Testing de Conectividad
```python
# tests/test_database_connectivity.py
import unittest
from django.test import TestCase
from django.db import connections
from productos.models import Productos

class DatabaseConnectivityTest(TestCase):
    @unittest.skipIf(
        not connections['default'].settings_dict['NAME'] == 'inventario',
        "Solo ejecutar con BD real"
    )
    def test_database_connection(self):
        """Verificar que la conexión a SQL Server funciona"""
        try:
            # Solo consulta de conectividad - no modifica datos
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
        except Exception as e:
            self.fail(f"Conexión a BD falló: {e}")
    
    @unittest.skipIf(
        not connections['default'].settings_dict['NAME'] == 'inventario',
        "Solo ejecutar con BD real"
    )
    def test_productos_table_exists(self):
        """Verificar que tabla Productos existe y es accesible"""
        try:
            # Solo lectura - count() no modifica datos
            count = Productos.objects.count()
            self.assertIsInstance(count, int)
            self.assertGreaterEqual(count, 0)
        except Exception as e:
            self.fail(f"Acceso a tabla Productos falló: {e}")
```

## Configuración pytest (Opcional)

### pytest.ini
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = inventario_web.tests_settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test* *Tests
python_functions = test_*
addopts = 
    --reuse-db
    --nomigrations
    --tb=short
    -v
```

### Dependencias de Testing
```txt
# Para testing avanzado (opcional)
pytest==7.4.0
pytest-django==4.5.2
pytest-mock==3.11.1
coverage==7.3.0
```

## Mocks y Stubs para Modelos

### Mock de Consultas ORM
```python
# tests/utils.py
from unittest.mock import MagicMock

def create_mock_producto(**kwargs):
    """Crear mock de producto con valores por defecto"""
    defaults = {
        'id_producto': 1,
        'title': 'Producto Test',
        'brand': 'Marca Test',
        'normal_price': 100.00,
        'sin_stock': False,
        'oferta': False,
    }
    defaults.update(kwargs)
    
    mock_producto = MagicMock()
    for key, value in defaults.items():
        setattr(mock_producto, key, value)
    
    return mock_producto

def mock_productos_queryset(productos_list):
    """Crear mock de queryset de productos"""
    mock_qs = MagicMock()
    mock_qs.count.return_value = len(productos_list)
    mock_qs.all.return_value = productos_list
    mock_qs.__iter__ = lambda x: iter(productos_list)
    return mock_qs
```

## Guardrails de Testing

### Restricciones Críticas
- ❌ **NUNCA** crear instancias reales de modelos `managed=False`
- ❌ **NUNCA** ejecutar `.save()`, `.create()`, `.delete()` en pruebas
- ❌ **NUNCA** usar fixtures que modifiquen BD externa
- ❌ **NUNCA** ejecutar migraciones en entorno de testing

### Restricciones de Datos
- ❌ **NUNCA** alterar datos reales en BD `inventario`
- ❌ **NUNCA** ejecutar truncate o drop en tablas
- ❌ **NUNCA** hacer transacciones sin rollback manual
- ❌ **NUNCA** depender de datos específicos de BD para tests

### Buenas Prácticas
- ✅ Usar mocks para consultas que no sean críticas
- ✅ Testing de lógica de negocio sin tocar BD
- ✅ Verificar status codes y templates
- ✅ Testing de formularios con datos simulados

## Sugerencias (No Aplicar Automáticamente)

### Testing de Integración con BD Separada
```python
# Para testing más completo, usar BD de testing separada
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'inventario_test',  # BD separada para testing
        'HOST': 'DESKTOP-AU48ANV',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
        },
    }
}

# Con modelos managed=True para testing
class ProductosTest(models.Model):
    # Misma estructura que Productos pero managed=True
    class Meta:
        managed = True
        db_table = 'productos_test'
```

### Coverage y Métricas
```cmd
# Instalar coverage
pip install coverage

# Ejecutar con coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Genera reporte HTML
```

### Testing de Performance
```python
# tests/test_performance.py
import time
from django.test import TestCase
from django.test.utils import override_settings

class PerformanceTest(TestCase):
    def test_dashboard_response_time(self):
        """Verificar que dashboard responde en tiempo razonable"""
        start_time = time.time()
        
        # Mock consultas para testing determinístico
        with patch('productos.models.Productos.objects'):
            response = self.client.get('/')
            
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, 1.0)  # Menos de 1 segundo
        self.assertEqual(response.status_code, 200)
```

---

**Guardrails para Copilot (bloque estándar):**
- No sugieras ejecutar `makemigrations` ni `migrate`.
- No propongas cambiar `managed=False` ni las PKs actuales.
- No introduzcas frameworks (DRF, React) ni pipelines de estáticos.
- No modifiques collation ni la conexión a SQL Server.
- No reestructures plantillas fuera de su ubicación actual.
- Si propones una mejora, ubícala en **"Sugerencias (no aplicar automáticamente)"**.