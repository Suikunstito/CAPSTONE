# SmartERP - Dockerfile Multi-Stage
# Este archivo define cómo construir la imagen de Docker para SmartERP

# =================================================================
# STAGE 1: Base - Python con dependencias del sistema
# =================================================================
FROM python:3.11-slim as base

# Metadatos de la imagen
LABEL maintainer="SmartERP Team"
LABEL description="SmartERP - Sistema Modular de Inventario Django"
LABEL version="1.0"

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para SQL Server
RUN apt-get update && apt-get install -y \
    # ODBC Driver para SQL Server
    curl \
    apt-transport-https \
    gnupg \
    unixodbc \
    unixodbc-dev \
    # Herramientas de compilación para algunos paquetes Python
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Instalar Microsoft ODBC Driver 17 para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN adduser --disabled-password --gecos '' appuser

# =================================================================
# STAGE 2: Builder - Instalación de dependencias Python
# =================================================================
FROM base as builder

# Crear directorio para instalar dependencias
WORKDIR /install

# Copiar archivos de dependencias
COPY requirements/ requirements/

# Instalar dependencias en directorio temporal
# (Esto permite optimizar capas de Docker)
RUN pip install --prefix=/install --no-warn-script-location \
    -r requirements/base.txt

# =================================================================
# STAGE 3: Development - Para desarrollo local
# =================================================================
FROM base as development

# Copiar dependencias instaladas desde builder stage
COPY --from=builder /install /usr/local

# Instalar dependencias adicionales de desarrollo
COPY requirements/development.txt /tmp/
RUN pip install --no-warn-script-location -r /tmp/development.txt

# Configurar directorio de trabajo
WORKDIR /app

# Cambiar a usuario no-root
USER appuser

# Puerto por defecto para desarrollo
EXPOSE 8000

# Comando por defecto - servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =================================================================
# STAGE 4: Production - Para producción optimizada
# =================================================================
FROM base as production

# Copiar dependencias instaladas desde builder stage
COPY --from=builder /install /usr/local

# Instalar dependencias adicionales de producción
COPY requirements/production.txt /tmp/
RUN pip install --no-warn-script-location -r /tmp/production.txt

# Configurar directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
# (En desarrollo usaremos volúmenes en lugar de COPY)
COPY --chown=appuser:appuser . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p staticfiles && chown appuser:appuser staticfiles

# Cambiar a usuario no-root
USER appuser

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Puerto para producción
EXPOSE 8000

# Comando por defecto - servidor de producción con Gunicorn
CMD ["gunicorn", "inventario_web.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "30", \
     "--keep-alive", "2", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]