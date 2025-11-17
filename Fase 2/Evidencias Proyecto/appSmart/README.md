# SmartERP - Sistema Modular de Inventario Django

Sistema de gestión de inventario empresarial con arquitectura modular, soporte para SQL Server/SQLite, y predicciones ML integradas.

---

## 🚀 Inicio Rápido

### Primera Vez - Configurar Entorno
```cmd
setup-dev.bat
```

### Ejecutar Servidor de Desarrollo  
```cmd
dev.bat
```

**El servidor se iniciará en:** http://127.0.0.1:8000/

📖 **[Guía Completa de Inicio](docs/GUIA-INICIO-RAPIDO.md)** - Instrucciones detalladas

---

## 📋 Comandos Principales

### Scripts en Raíz (Entrada Principal)
| Comando | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `setup-dev.bat` | ⚙️ Configurar entorno | **Solo la primera vez** |
| `dev.bat` | 🚀 Iniciar desarrollo | **Uso diario** |

### Scripts Auxiliares (`scripts/`)
| Comando | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `scripts\dev-local.bat` | 💻 Forzar modo local | Sin Docker |
| `scripts\test.bat` | 🧪 Ejecutar tests | Verificar código |
| `scripts\prod.bat` | 🏭 Modo producción | Deploy con Docker |
| `scripts\clean.bat` | 🧹 Limpiar entorno | Reset completo |

### Auto-Detección Inteligente
`dev.bat` detecta automáticamente:
- ✅ **Docker disponible** → Usa Docker Compose  
- ✅ **Docker no disponible** → Usa entorno local Python
- ✅ **Sin configuración manual** → Todo automático

---

## 🎯 Integración VSCode

Presiona `Ctrl+Shift+P` → `Tasks: Run Task`:

- 🚀 **SmartERP: Desarrollo (Auto-detecta)** - Ejecutar desarrollo
- ⚙️ **SmartERP: Configurar Desarrollo** - Setup inicial  
- 💻 **SmartERP: Desarrollo (Solo Local)** - Sin Docker
- 🧪 **SmartERP: Ejecutar Tests** - Suite de tests
- 🏭 **SmartERP: Producción** - Deploy producción
- 🧹 **SmartERP: Limpiar Entorno** - Reset completo

---

## 🏗️ Arquitectura del Proyecto

### Estructura Modular por Dominios

```
appSmart/
├── 📄 README.md                    # Documentación principal
├── 📁 .github/                     # GitHub config y docs internas
│   └── docs/                       # Documentación de desarrollo
├── 📁 docs/                        # Documentación del proyecto
│   ├── README.md                   # Índice de documentación
│   ├── GUIA-INICIO-RAPIDO.md      # Setup y comandos
│   └── CONFIGURACION-BASE-DATOS.md # Configuración BD
├── 📁 scripts/                     # Scripts auxiliares
│   ├── dev-local.bat              # Forzar desarrollo local
│   ├── test.bat                   # Tests
│   ├── prod.bat                   # Producción
│   └── clean.bat                  # Limpieza
├── 🔧 setup-dev.bat                # Script de configuración inicial
├── 🚀 dev.bat                      # Script principal de desarrollo
├── 📁 users/                       # � Autenticación
├── 📁 catalog/                     # 📦 Productos y catálogo
├── 📁 inventory/                   # � Inventario y dashboard
├── 📁 sales/                       # 💰 Ventas y transacciones
└── 📁 inventario_web/              # ⚙️ Config Django principal

Django Apps:
users/
├── views.py           # CustomLoginView, CustomLogoutView
├── urls.py            # /login/, /logout/
└── templates/users/   # Templates de autenticación

catalog/
├── models/products.py # Modelo Productos (managed=False)
├── views.py           # CRUD productos
├── forms/products.py  # ProductoForm
└── urls.py            # /productos/*

inventory/
├── models/movements.py        # StgProductosRaw + movimientos futuros
├── views.py                   # Dashboard con estadísticas
├── services/predictions.py    # Sistema de predicciones ML
└── urls.py                    # / (dashboard raíz)

sales/
├── models/sales.py    # Modelo Ventas (managed=False)
├── views.py           # Placeholder ventas
└── urls.py            # Rutas futuras ventas
```

### Tecnologías

- **Backend:** Django 5.2+ con arquitectura modular
- **Base de Datos:** SQL Server (producción) / SQLite (desarrollo)
- **Cache:** Redis (opcional, Docker)
- **ML:** Sistema de predicciones integrado para inventario
- **Frontend:** Templates Django con Bootstrap
- **Deploy:** Docker + Docker Compose

---

## 🗄️ Base de Datos

### Configuración Inteligente con Fallback Automático

SmartERP detecta automáticamente la disponibilidad de SQL Server:
- **SQL Server disponible** → Se conecta automáticamente
- **SQL Server no disponible** → Usa SQLite para desarrollo local

### Cambiar entre Bases de Datos

Editar `.env.development`:

**Para usar SQLite (actual):**
```bash
FORCE_SQLITE=True
```

**Para usar SQL Server:**
```bash
# FORCE_SQLITE=False
```

📖 **[Guía Completa de Base de Datos](docs/CONFIGURACION-BASE-DATOS.md)** - Configuración detallada

---

## 🐳 Docker (Opcional)

### Ventajas
- ✅ Portabilidad total entre sistemas operativos
- ✅ Aislamiento completo del entorno
- ✅ Configuración automática de servicios
- ✅ Reproducibilidad garantizada

### Arquitectura Docker
```
Docker Containers:
├── smarterp (Django App)     # Aplicación principal
├── redis (Cache)             # Cache y sesiones
└── nginx (Producción)        # Servidor web

Conecta a:
└── SQL Server (Host/Container)  # Base de datos
```

### Ejecutar con Docker
```cmd
# Desarrollo con Docker
dev.bat              # Auto-detecta y usa Docker si está disponible

# Producción con Docker
prod.bat
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[Guía de Inicio Rápido](docs/GUIA-INICIO-RAPIDO.md)** | Setup, comandos y troubleshooting |
| **[Configuración de Base de Datos](docs/CONFIGURACION-BASE-DATOS.md)** | SQLite vs SQL Server |
| **[Instrucciones Copilot](.github/copilot-instructions.md)** | Guía para desarrollo con GitHub Copilot |

---

## � Desarrollo

### Flujo de Trabajo Típico

```cmd
# 1. Primera vez: Setup
setup-dev.bat

# 2. Desarrollo diario
dev.bat                 # Iniciar servidor (auto-reload activado)

# 3. Ejecutar tests
test.bat

# 4. Comandos Django útiles
venv_smarterp\Scripts\activate.bat
python manage.py check
python manage.py shell
python manage.py createsuperuser
```

### Comandos Django

```cmd
# Activar entorno virtual
venv_smarterp\Scripts\activate.bat

# Verificar configuración
python manage.py check

# Shell interactivo
python manage.py shell

# Crear superusuario
python manage.py createsuperuser

# Aplicar migraciones (solo tablas de Django: auth, admin, etc.)
python manage.py migrate
```

### Modelos con `managed=False`

**IMPORTANTE:** Los modelos de SmartERP tienen `managed=False`:
- Django NO creará ni modificará estas tablas
- Las tablas son gestionadas externamente (SQL Server)
- Solo se aplican migraciones de Django (auth, admin, sessions)

---

## 🆘 Solución de Problemas

### Error: "Python no encontrado"
```cmd
python --version
# Si falla, instalar Python desde: https://www.python.org/downloads/
```

### Error: "venv_smarterp no encontrado"
```cmd
setup-dev.bat
```

### Error: Base de datos no conecta
```cmd
# Editar .env.development
FORCE_SQLITE=True

# Reiniciar servidor
dev.bat
```

### Reset Completo
```cmd
clean.bat              # Limpia todo
setup-dev.bat          # Reconfigura
dev.bat                # Ejecuta
```

---

## 📊 Características

### Funcionalidades Actuales
- ✅ Autenticación de usuarios (login/logout)
- ✅ Gestión de catálogo de productos (CRUD)
- ✅ Dashboard con estadísticas de inventario
- ✅ Sistema de predicciones ML para compras
- ✅ Reportes CSV exportables
- ✅ Base de datos flexible (SQL Server/SQLite)
- ✅ Arquitectura modular escalable

### Módulos del Sistema
- **Users:** Autenticación y gestión de usuarios
- **Catalog:** Gestión completa de productos
- **Inventory:** Dashboard, estadísticas y predicciones ML
- **Sales:** Estructura base para gestión de ventas (extensible)

---

## 🚀 Producción

### Deploy con Docker

```cmd
# Configurar variables de producción
# Editar .env.production

# Ejecutar en modo producción
prod.bat
```

### Configuración Producción

1. Configurar `.env.production` con valores reales
2. Verificar conexión SQL Server
3. Configurar `DJANGO_ALLOWED_HOSTS`
4. Establecer `DJANGO_DEBUG=False`
5. Generar `SECRET_KEY` segura
6. Configurar HTTPS y certificados

---

## 💡 Ventajas del Sistema

- ✅ **Sin dependencias externas complejas** - Solo Python + Scripts nativos
- ✅ **Auto-detección inteligente** - Docker o Local automático  
- ✅ **Integración VSCode nativa** - Sin extensiones adicionales
- ✅ **Base de datos flexible** - SQL Server o SQLite según disponibilidad
- ✅ **Arquitectura modular** - Fácil de extender y mantener
- ✅ **Scripts simples** - Fácil de entender y personalizar
- ✅ **Documentación completa** - Guías para cada aspecto del sistema

---

## 📝 Licencia

[Especificar licencia del proyecto]

## 👥 Contribuciones

[Especificar guía de contribución]

---

**SmartERP** - Sistema empresarial modular y escalable para gestión de inventario 🎉