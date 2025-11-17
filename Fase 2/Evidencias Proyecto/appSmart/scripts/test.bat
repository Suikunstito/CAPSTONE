@echo off
REM ============================================================================
REM SmartERP - Ejecutar Tests
REM ============================================================================
echo [SmartERP] Ejecutando tests...

if not exist "venv_smarterp" (
    echo [ERROR] Entorno virtual no encontrado
    echo [SOLUCION] Ejecutar 'setup-dev.bat' primero
    pause
    exit /b 1
)

call venv_smarterp\Scripts\activate.bat
set DJANGO_ENVIRONMENT=testing

echo [TEST] Ejecutando tests de Django...
python manage.py test

echo.
echo [SmartERP] Tests completados
pause