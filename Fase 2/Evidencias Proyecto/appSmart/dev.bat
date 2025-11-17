@echo off
REM ============================================================================
REM SmartERP - Iniciar Servidor de Desarrollo (Auto-detecta Docker/Local)
REM ============================================================================
echo [SmartERP] Iniciando servidor de desarrollo...

REM Auto-detectar Docker
echo [INFO] Verificando Docker...
docker version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Docker no disponible, usando entorno local
    goto :local_dev
)

docker info >nul 2>&1  
if errorlevel 1 (
    echo [INFO] Docker daemon no esta corriendo, usando entorno local
    echo [TIP] Para usar Docker: Iniciar Docker Desktop
    goto :local_dev
)

echo [INFO] Docker disponible, usando Docker
goto :docker_dev

:docker_dev
echo [DOCKER] Iniciando con Docker Compose...
docker-compose up --remove-orphans
goto :end

:local_dev
echo [LOCAL] Iniciando en modo local...
if not exist "venv_smarterp" (
    echo [ERROR] Entorno virtual no encontrado
    echo [SOLUCION] Ejecutar 'setup-dev.bat' primero
    pause
    exit /b 1
)

call venv_smarterp\Scripts\activate.bat
set DJANGO_ENVIRONMENT=development
python manage.py runserver
goto :end

:end
echo.
echo [SmartERP] Servidor detenido
pause