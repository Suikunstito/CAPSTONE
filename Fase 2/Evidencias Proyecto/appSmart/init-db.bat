@echo off
REM SmartERP - Inicializar Base de Datos SQLite
REM Crea tablas y datos de prueba para desarrollo local

echo ========================================
echo SmartERP - Inicializar SQLite
echo ========================================
echo.

REM Verificar entorno virtual
if not exist "venv_smarterp\Scripts\python.exe" (
    echo [ERROR] Entorno virtual no encontrado
    echo Ejecuta primero: setup-dev.bat
    pause
    exit /b 1
)

REM Ejecutar script de inicialización
echo Ejecutando script de inicialización...
echo.
venv_smarterp\Scripts\python.exe scripts\init_sqlite_db.py

echo.
pause
