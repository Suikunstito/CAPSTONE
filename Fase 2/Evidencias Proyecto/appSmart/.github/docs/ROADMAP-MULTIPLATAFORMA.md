# SmartERP - Roadmap de Escalabilidad Multiplataforma

## Visión General
Evolución de SmartERP desde aplicación web Django hacia sistema multiplataforma con arquitectura API-first, **sin reescribir código existente**.

---

## 🏗️ Arquitectura de Escalabilidad

### Fase 1: Web Tradicional (ACTUAL ✅)
**Duración**: Ya implementado
**Stack**: Django Templates + Modular Architecture
**Beneficio**: Sistema funcional en producción inmediata

```
Usuario Web
     ↓
Django Templates (Views)
     ↓
Services (Lógica de negocio) ← ¡Ya modular!
     ↓
Models (ORM)
     ↓
SQL Server
```

### Fase 2: API REST Backend (3-6 meses)
**Stack**: Django REST Framework + JWT
**Sin romper**: Web actual sigue funcionando

```
Usuario Web          App Móvil        Desktop
    ↓                    ↓                ↓
Django Templates    REST API         REST API
    ↓                    ↓                ↓
      Services compartidos (Lógica única)
              ↓
          Models (ORM)
              ↓
          SQL Server
```

**Nueva estructura**:
```
appSmart/
├── api/                        # Nueva app Django REST
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py                # /api/v1/*
│   ├── permissions.py         # Permisos JWT
│   ├── pagination.py          # Paginación estándar
│   ├── v1/                    # Versionado API
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── users/
│   │   │   ├── serializers.py # UserSerializer
│   │   │   └── views.py       # Login, Register, Profile
│   │   ├── catalog/
│   │   │   ├── serializers.py # ProductoSerializer
│   │   │   └── views.py       # CRUD productos
│   │   ├── inventory/
│   │   │   ├── serializers.py # StockSerializer
│   │   │   └── views.py       # Stats, Movimientos
│   │   └── sales/
│   │       ├── serializers.py # VentaSerializer
│   │       └── views.py       # Registro ventas
│   └── tests/                 # Tests API
├── catalog/                   # MANTIENE templates web
├── inventory/                 # MANTIENE dashboard web
└── sales/                     # MANTIENE views web
```

### Fase 3: Clientes Multiplataforma (6-12 meses)
**Clientes**: Flutter/React Native (móvil) + Electron (desktop)
**Backend**: API única reutilizada

```
Web (Django)    Móvil (Flutter)    Desktop (Electron)
     ↓                ↓                    ↓
     └────────────── REST API ────────────┘
                      ↓
              Services + Models
                      ↓
                 SQL Server
```

---

## 📋 Implementación por Fases

### **Fase 2.1: Setup Django REST Framework**

**1. Instalar dependencias**:
```bash
pip install -r requirements/api.txt
```

**2. Actualizar settings.py**:
```python
INSTALLED_APPS = [
    # ...apps actuales...
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',  # Documentación OpenAPI
    'api',  # Nueva app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Antes de CommonMiddleware
    # ...resto middleware...
]

# Configuración REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# CORS para apps móviles/desktop (ajustar en producción)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React/Electron local
    "http://localhost:8081",  # React Native Expo
]
```

**3. Crear app API**:
```bash
python manage.py startapp api
```

### **Fase 2.2: Endpoints Básicos (Ejemplo: Productos)**

**api/v1/catalog/serializers.py**:
```python
from rest_framework import serializers
from catalog.models.products import Productos

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = ['id_producto', 'title', 'brand', 'normal_price', 
                  'low_price', 'oferta', 'categoria1', 'sin_stock']
        read_only_fields = ['id_producto', 'datetime']
    
    def validate_normal_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Precio no puede ser negativo")
        return value

class ProductoDetailSerializer(ProductoSerializer):
    """Serializer con más detalle para endpoints individuales"""
    class Meta(ProductoSerializer.Meta):
        fields = ProductoSerializer.Meta.fields + [
            'high_price', 'categoria2', 'ahorro', 'ahorro_percent', 'kilo'
        ]
```

**api/v1/catalog/views.py**:
```python
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from catalog.models.products import Productos
from catalog.services.products import get_product_stats  # Reutiliza servicios
from .serializers import ProductoSerializer, ProductoDetailSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestión de productos
    
    list: Listar todos los productos (con paginación)
    retrieve: Obtener detalle de un producto
    create: Crear nuevo producto
    update: Actualizar producto existente
    destroy: Eliminar producto
    """
    queryset = Productos.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'brand', 'categoria1']
    ordering_fields = ['normal_price', 'datetime']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetailSerializer
        return ProductoSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Endpoint adicional: GET /api/v1/productos/stats/"""
        stats = get_product_stats()  # ← Reutiliza servicio existente
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def sin_stock(self, request):
        """Productos sin stock"""
        productos = self.queryset.filter(sin_stock=True)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
```

**api/v1/urls.py**:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .catalog.views import ProductoViewSet
from .inventory.views import InventoryViewSet
from .sales.views import VentaViewSet

router = DefaultRouter()
router.register('productos', ProductoViewSet, basename='producto')
router.register('inventario', InventoryViewSet, basename='inventario')
router.register('ventas', VentaViewSet, basename='venta')

urlpatterns = [
    path('', include(router.urls)),
]
```

**api/urls.py**:
```python
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Autenticación JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Versión 1 API
    path('v1/', include('api.v1.urls')),
    
    # Documentación OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

**inventario_web/urls.py** (agregar):
```python
urlpatterns = [
    # ...URLs actuales web...
    path('api/', include('api.urls')),  # Nueva ruta API
]
```

### **Fase 2.3: Testing API**

**api/tests/test_productos.py**:
```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from catalog.models.products import Productos

class ProductoAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'password')
        self.client.force_authenticate(user=self.user)
        
    def test_list_productos(self):
        response = self.client.get('/api/v1/productos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_producto(self):
        data = {
            'title': 'Producto Test',
            'brand': 'Marca Test',
            'normal_price': 10.99,
            'sin_stock': False
        }
        response = self.client.post('/api/v1/productos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

---

## 🚀 Fase 3: Clientes Multiplataforma

### **Opción A: Flutter (Móvil + Desktop + Web)**
**Ventaja**: Un solo código para Android, iOS, Windows, macOS, Linux, Web

```dart
// Ejemplo de consumo API
class ProductoService {
  final String baseUrl = 'http://tu-servidor.com/api/v1';
  String? _token;

  Future<List<Producto>> getProductos() async {
    final response = await http.get(
      Uri.parse('$baseUrl/productos/'),
      headers: {'Authorization': 'Bearer $_token'},
    );
    return (jsonDecode(response.body) as List)
        .map((json) => Producto.fromJson(json))
        .toList();
  }
}
```

### **Opción B: React Native (Móvil) + Electron (Desktop)**
**Ventaja**: Ecosistema JavaScript compartido

```typescript
// Ejemplo consumo API
const API_URL = 'http://tu-servidor.com/api/v1';

export const getProductos = async (token: string) => {
  const response = await fetch(`${API_URL}/productos/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};
```

### **Opción C: Progressive Web App (PWA)**
**Ventaja**: Funciona offline, instalable, cero distribución

```javascript
// Service Worker para cache offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

---

## 📊 Comparativa de Tecnologías

| Característica | Flutter | React Native + Electron | PWA |
|----------------|---------|-------------------------|-----|
| **Código compartido** | 95% | 70-80% | 100% web |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Ecosistema** | Dart | JavaScript/TypeScript | JavaScript |
| **Curva aprendizaje** | Media | Baja (si sabes JS) | Baja |
| **Distribución** | App Stores | App Stores + descarga | Sin distribución |
| **Offline** | ✅ Nativo | ✅ Nativo | ✅ Service Workers |
| **Tamaño app** | ~20MB | ~50MB (Electron) | ~1MB |
| **Recomendado para** | Startups, MVP | Equipos JS | Validación rápida |

---

## 🎯 Recomendación Final para SmartERP

### **Mi Sugerencia: Flutter**

**Razones**:
1. **Un solo código** para móvil (Android/iOS) y desktop (Windows/Mac/Linux)
2. **Performance nativa** crucial para inventario en tiempo real
3. **Dart es fácil** si sabes Python (similar sintaxis)
4. **Material Design** out-of-the-box para UI consistente
5. **Hot reload** = desarrollo rápido como Django

**Roadmap Realista**:
```
Mes 1-2:   Implementar API REST (Fase 2.1-2.2)
Mes 3-4:   App móvil Flutter (lectura inventario, escaneo códigos)
Mes 5-6:   App desktop Flutter (gestión completa)
Mes 7+:    Features avanzadas (sincronización offline, reportes)
```

---

## ✅ Ventajas de Tu Arquitectura Actual

**Ya tienes**:
- ✅ Servicios modulares → Fácil crear serializers
- ✅ Lógica separada de vistas → Reutilizable en API
- ✅ Modelos unmanaged → API no rompe esquema SQL
- ✅ Dominio separado → API versión 1 espeja tu estructura

**NO necesitas**:
- ❌ Reescribir código existente
- ❌ Migrar base de datos
- ❌ Cambiar arquitectura
- ❌ Perder funcionalidad web actual

---

## 📝 Próximos Pasos Inmediatos

1. **Experimentar con API básica** (2-3 días):
   ```bash
   pip install -r requirements/api.txt
   python manage.py startapp api
   # Implementar ProductoViewSet básico
   ```

2. **Documentación automática** (1 día):
   - Configurar drf-spectacular
   - Acceder a `/api/docs/` para ver Swagger UI

3. **Cliente prueba** (3-5 días):
   - Crear app Flutter básica
   - Conectar a `/api/v1/productos/`
   - Probar autenticación JWT

4. **Decisión arquitectura móvil** (1 semana):
   - Evaluar Flutter vs React Native
   - Prototipos UI con datos reales

---

## 🔗 Recursos Recomendados

- [Django REST Framework Official](https://www.django-rest-framework.org/)
- [Flutter Cookbook](https://docs.flutter.dev/cookbook)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [API Design Patterns](https://restfulapi.net/)

---

**Última actualización**: 2025-11-11
**Versión SmartERP**: Modular v2.0 (Post-refactor)
