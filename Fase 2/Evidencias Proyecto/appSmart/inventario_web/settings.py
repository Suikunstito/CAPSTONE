from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración por ambiente - SmartERP
def _load_environment_config():
    """Carga configuración según ambiente (development/production)"""
    # Determinar ambiente
    environment = os.getenv('DJANGO_ENVIRONMENT', 'development')
    
    # Archivos de configuración por orden de prioridad
    env_files = [
        BASE_DIR / f'.env.{environment}',  # Específico del ambiente
        BASE_DIR / '.env.local',           # Local override (gitignored)
        BASE_DIR / '.env',                 # Fallback general
    ]
    
    for env_file in env_files:
        _load_dotenv(env_file)
    
    print(f"[SmartERP] Configuración cargada para ambiente: {environment}")

def _load_dotenv(path: Path):
    """Carga variables de entorno desde archivo"""
    try:
        if path.exists():
            print(f"[SmartERP] Cargando configuración: {path.name}")
            with path.open('r', encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key, value)
    except Exception as e:
        print(f"[SmartERP] Advertencia cargando {path}: {e}")

# Cargar configuración por ambiente
_load_environment_config()

# Security
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-p5zbjum!u&)rw=6vcw9_qx5^-7#(+q!el#c9d#-kcxzt50&5!0'
)

# SECURITY WARNING: set DJANGO_DEBUG=False in production
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')

# Comma-separated list in env: e.g. "example.com,api.example.com"
_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _hosts_env.split(',') if h.strip()]

# Application definition - ARQUITECTURA MODULAR SmartERP
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventario_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Templates globales
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

WSGI_APPLICATION = 'inventario_web.wsgi.application'

# Database - Configuración inteligente con fallback automático
def _configure_database():
    """
    Configura base de datos con fallback automático:
    1. Intenta SQL Server si está configurado
    2. Si SQL Server falla, usa SQLite para desarrollo local
    """
    db_engine = os.getenv('DB_ENGINE', 'mssql')
    use_sqlite_fallback = os.getenv('USE_SQLITE_FALLBACK', 'True').lower() in ('1', 'true', 'yes', 'on')
    force_sqlite = os.getenv('FORCE_SQLITE', 'False').lower() in ('1', 'true', 'yes', 'on')
    
    # Forzar SQLite si está configurado
    if force_sqlite or db_engine == 'sqlite3':
        return _get_sqlite_config()
    
    # Configuración SQL Server con validación
    if db_engine == 'mssql':
        db_host = os.getenv('DB_HOST', '')
        
        # Si no hay host configurado, usar SQLite
        if not db_host or db_host == 'localhost':
            print("[SmartERP] ⚠️  DB_HOST no configurado para SQL Server")
            if DEBUG and use_sqlite_fallback:
                print("[SmartERP] 🔄 Usando SQLite para desarrollo local...")
                return _get_sqlite_config()
        
        # Verificar disponibilidad de pyodbc y drivers
        if DEBUG and use_sqlite_fallback:
            try:
                import pyodbc
                available_drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
                
                if not available_drivers:
                    print("[SmartERP] ⚠️  No se encontraron drivers ODBC para SQL Server")
                    print("[SmartERP] � Instala 'ODBC Driver 17 for SQL Server'")
                    print("[SmartERP] 🔄 Usando SQLite para desarrollo local...")
                    return _get_sqlite_config()
                
                print(f"[SmartERP] 🔍 Configurando SQL Server: {db_host}")
                print("[SmartERP] ℹ️  Si la conexión falla al iniciar, usa: FORCE_SQLITE=True")
                
            except ImportError:
                print("[SmartERP] ⚠️  pyodbc no instalado")
                print("[SmartERP] 🔄 Usando SQLite para desarrollo local...")
                return _get_sqlite_config()
            except Exception as e:
                print(f"[SmartERP] ⚠️  Error verificando SQL Server: {e}")
                print("[SmartERP] 🔄 Usando SQLite para desarrollo local...")
                return _get_sqlite_config()
        
        # Retornar configuración SQL Server
        return {
            'ENGINE': 'mssql',
            'NAME': os.getenv('DB_NAME', 'inventario'),  
            'HOST': db_host,  
            'PORT': os.getenv('DB_PORT', ''),  
            'USER': os.getenv('DB_USER', ''),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'OPTIONS': {
                'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
                'Trusted_Connection': os.getenv('DB_TRUSTED_CONNECTION', 'yes'),
                'TrustServerCertificate': os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes'),
            }
        }
    
    # Engine no reconocido
    print(f"[SmartERP] ⚠️  DB_ENGINE '{db_engine}' no reconocido, usando SQLite")
    return _get_sqlite_config()

def _get_sqlite_config():
    """Configuración SQLite para desarrollo local"""
    sqlite_path = BASE_DIR / 'db_smarterp_local.sqlite3'
    print(f"[SmartERP] 💾 Base de datos SQLite: {sqlite_path.name}")
    print("[SmartERP] ℹ️  Los modelos tienen managed=False - Tablas no se crean automáticamente")
    print("[SmartERP] 💡 Para usar SQL Server, verifica la configuración en .env.development")
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': sqlite_path,
    }

DATABASES = {
    'default': _configure_database()
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-cl'  # Chile locale
TIME_ZONE = 'America/Santiago'  # Chile timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
_static_dir = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [_static_dir] if os.path.isdir(_static_dir) else []

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF Trusted Origins (configurar en despliegue si usas HTTPS y dominios)
_csrf_env = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if _csrf_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(',') if o.strip()]