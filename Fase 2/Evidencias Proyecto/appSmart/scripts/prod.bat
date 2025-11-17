@echo off
REM ============================================================================
REM SmartERP - Produccion con Docker
REM ============================================================================
echo [SmartERP] Iniciando en modo produccion...

REM Verificar Docker
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no encontrado
    echo [SOLUCION] Instalar Docker Desktop
    pause
    exit /b 1
)

echo [PROD] Construyendo imagen de produccion...
docker-compose -f docker-compose.prod.yml build

echo [PROD] Iniciando servicios en modo produccion...
docker-compose -f docker-compose.prod.yml up -d

echo.
echo [SUCCESS] SmartERP ejecutandose en modo produccion
echo [INFO] Acceder en: http://localhost
echo [INFO] Para detener: docker-compose -f docker-compose.prod.yml down
echo.
pause