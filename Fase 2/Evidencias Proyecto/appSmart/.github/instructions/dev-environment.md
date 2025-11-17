# Entorno de Desarrollo - Configuración Local

## Requisitos del Sistema

### Componentes Obligatorios
| Componente              | Versión Mínima    | Propósito                          | Estado    |
|-------------------------|-------------------|------------------------------------|-----------|
| Python                  | 3.8+              | Runtime Django                     | Requerido |
| SQL Server              | 2016+             | Base de datos principal            | Requerido |
| ODBC Driver 17          | Actual            | Conectividad SQL Server            | Requerido |
| Django                  | 5.2+              | Framework web                      | Requerido |
| python-dotenv           | Cualquiera        | Variables de entorno               | Instalado |

### Verificación de Instalación
```cmd
# Verificar Python
python --version

# Verificar Django
python -m django --version

# Verificar driver ODBC (Windows)
odbcad32.exe
# Buscar: "ODBC Driver 17 for SQL Server"

# Verificar conectividad SQL Server
sqlcmd -S DESKTOP-AU48ANV -E
```

## Configuración de Variables de Entorno

### Archivo .env Esperado
```bash
# .env en la raíz del proyecto
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Variables opcionales para producción
# SECRET_KEY=tu-secret-key-de-produccion
# ALLOWED_HOSTS=midominio.com,www.midominio.com
```

### Variables por Entorno
| Variable        | Desarrollo    | Producción              | Descripción                  |
|-----------------|---------------|-------------------------|------------------------------|
| `DEBUG`         | `True`        | `False`                 | Modo debug Django            |
| `ALLOWED_HOSTS` | `*`           | Lista específica        | Hosts permitidos             |
| `SECRET_KEY`    | Hardcoded     | Variable segura         | Clave secreta Django         |

### Carga de Variables
```python
# En settings.py (ya implementado)
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
```

## Comandos de Arranque

### Desarrollo Local - Pasos
1. **Abrir terminal** en directorio del proyecto
2. **Verificar conexión BD**:
   ```cmd
   python manage.py shell
   >>> from productos.models import Productos
   >>> Productos.objects.count()
   # Debe retornar un número sin errores
   ```
3. **Iniciar servidor**:
   ```cmd
   python manage.py runserver
   # Servidor en: http://127.0.0.1:8000
   ```

### Comandos de Verificación
```cmd
# Verificar configuración Django
python manage.py check

# Verificar sintaxis de configuración
python manage.py check --deploy

# Consola interactiva Django
python manage.py shell

# Crear superusuario para /admin (opcional)
python manage.py createsuperuser
```

## Troubleshooting Conexión SQL Server

### Errores Comunes y Soluciones

#### Error: "Can't connect to SQL Server"
```cmd
# Verificar estado del servicio
services.msc
# Buscar: SQL Server (MSSQLSERVER) - debe estar "Ejecutándose"

# Verificar puerto (default 1433)
netstat -an | findstr 1433

# Probar conexión manual
sqlcmd -S DESKTOP-AU48ANV -E -Q "SELECT 1"
```

#### Error: "ODBC Driver not found"
```cmd
# Descargar e instalar desde Microsoft:
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Verificar instalación
reg query "HKLM\SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 17 for SQL Server"
```

#### Error: "Database 'inventario' doesn't exist"
```sql
-- Conectar a SQL Server como administrador
sqlcmd -S DESKTOP-AU48ANV -E

-- Verificar bases existentes
SELECT name FROM sys.databases;
GO

-- Crear base si no existe (solo si es necesario)
CREATE DATABASE inventario;
GO
```

#### Error: "Collation not supported"
```sql
-- Verificar collation del servidor
SELECT SERVERPROPERTY('Collation');

-- Verificar collation de la base
SELECT collation_name FROM sys.databases WHERE name = 'inventario';

-- Debe incluir 'Modern_Spanish_CI_AS' o ser compatible
```

### Configuración ODBC Windows

#### Via odbcad32.exe
1. Ejecutar `odbcad32.exe` como administrador
2. Pestaña "System DSN" → "Add"
3. Seleccionar "ODBC Driver 17 for SQL Server"
4. Configurar:
   - **Name**: `InventarioDSN`
   - **Server**: `DESKTOP-AU48ANV`
   - **Authentication**: Windows Authentication
5. Test Connection → Success

## Configuración de Red (SQL Server)

### SQL Server Configuration Manager
1. **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
2. **TCP/IP** → **Enabled**: Yes
3. **TCP/IP Properties** → **IP Addresses**:
   - **IPAll** → **TCP Port**: 1433
4. **Restart SQL Server service**

### Windows Firewall
```cmd
# Agregar regla para puerto 1433
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433

# Verificar regla
netsh advfirewall firewall show rule name="SQL Server"
```

## Estructura de Directorios de Desarrollo

### Setup Recomendado
```
C:\Proyectos\
└── appSmart\
    ├── .env                    # Variables de entorno (no commitear)
    ├── .gitignore              # Ignorar .env, __pycache__, etc.
    ├── manage.py
    ├── db.sqlite3              # SQLite no usado, ignorar
    ├── inventario_web\
    ├── productos\
    └── .github\instructions\   # Documentación modular
```

### .gitignore Sugerido
```gitignore
# Variables de entorno
.env

# Django
__pycache__/
*.pyc
*.pyo
db.sqlite3

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

## Dependencias y Paquetes

### Instalación Manual (Estado Actual)
```cmd
# Sin requirements.txt - instalar globalmente
pip install Django==5.2.*
pip install python-dotenv
pip install django-mssql
# O pip install mssql (verificar driver específico usado)
```

### Dependencias del Sistema Windows
- **Microsoft Visual C++ Redistributable** (para drivers SQL)
- **Windows Authentication** configurada para el usuario actual
- **Permisos de red** para acceder a `DESKTOP-AU48ANV`

## Guardrails de Entorno

### Restricciones de Configuración
- ❌ **NUNCA** subir `.env` al repositorio
- ❌ **NUNCA** cambiar `DESKTOP-AU48ANV` sin coordinar con equipo
- ❌ **NUNCA** exponer SECRET_KEY en código fuente
- ❌ **NUNCA** alterar configuración ODBC sin backup

### Restricciones de Base de Datos
- ❌ **NUNCA** ejecutar scripts DDL desde Django
- ❌ **NUNCA** cambiar configuración de collation
- ❌ **NUNCA** modificar permisos de BD desde aplicación
- ❌ **NUNCA** usar conexiones no autenticadas

## Sugerencias (No Aplicar Automáticamente)

### Mejoras de Configuración
```python
# requirements.txt sugerido
Django==5.2.8
python-dotenv==1.0.0
django-mssql==1.2.0  # Verificar package exacto usado

# Para desarrollo adicional:
# pytest-django==4.5.2
# django-debug-toolbar==4.2.0
```

### Configuración de Desarrollo Avanzada
```python
# settings_dev.py (separar configuraciones)
from .settings import *

# Solo en desarrollo
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Logging detallado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Scripts de Automatización
```cmd
:: start_dev.bat
@echo off
echo Verificando conexión a SQL Server...
python manage.py shell -c "from productos.models import Productos; print(f'Productos en BD: {Productos.objects.count()}')"
if %errorlevel% neq 0 (
    echo ERROR: No se puede conectar a la base de datos
    pause
    exit /b 1
)
echo Iniciando servidor Django...
python manage.py runserver
```

### Docker Local (Opcional)
```dockerfile
# Dockerfile sugerido para desarrollo
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

**Guardrails para Copilot (bloque estándar):**
- No sugieras ejecutar `makemigrations` ni `migrate`.
- No propongas cambiar `managed=False` ni las PKs actuales.
- No introduzcas frameworks (DRF, React) ni pipelines de estáticos.
- No modifiques collation ni la conexión a SQL Server.
- No reestructures plantillas fuera de su ubicación actual.
- Si propones una mejora, ubícala en **"Sugerencias (no aplicar automáticamente)"**.