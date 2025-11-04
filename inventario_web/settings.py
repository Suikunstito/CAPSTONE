from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Simple .env loader (sin dependencia externa)
def _load_dotenv(path: Path):
    try:
        if path.exists():
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
    except Exception:
        # No romper settings si hay error leyendo .env
        pass

_load_dotenv(BASE_DIR / '.env')


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


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'productos',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # carpeta global
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


# Database
# Requires mssql-django and an installed ODBC driver
DB_ENGINE = os.getenv('DB_ENGINE', 'mssql')
DB_OPTIONS = {}
if DB_ENGINE == 'mssql':
    DB_OPTIONS = {
        'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server'),
        'Trusted_Connection': os.getenv('DB_TRUSTED_CONNECTION', 'yes'),
        'TrustServerCertificate': os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes'),
    }

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.getenv('DB_NAME', 'inventario'),  # nombre de la base de datos
        'HOST': os.getenv('DB_HOST', 'AOANBC02CW0729\\SQLEXPRESS'),  # servidor o instancia
        'PORT': os.getenv('DB_PORT', ''),  # vacío = puerto por defecto
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
    }
}
if DB_OPTIONS:
    DATABASES['default']['OPTIONS'] = DB_OPTIONS


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
# Directorio de recopilación para despliegue (collectstatic)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Directorios adicionales de archivos estáticos en desarrollo
_static_dir = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [_static_dir] if os.path.isdir(_static_dir) else []


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CSRF Trusted Origins (configurar en despliegue si usas HTTPS y dominios)
# Env var: DJANGO_CSRF_TRUSTED_ORIGINS="https://example.com,https://www.example.com"
_csrf_env = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if _csrf_env:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(',') if o.strip()]
