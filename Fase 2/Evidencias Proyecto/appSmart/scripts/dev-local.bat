@echo off
REM ============================================================================
REM SmartERP - Iniciar en Modo Local (sin Docker)
REM ============================================================================
echo [SmartERP] Iniciando servidor en modo local...

if not exist "venv_smarterp" (
    echo [ERROR] Entorno virtual no encontrado
    echo [SOLUCION] Ejecutar 'setup-dev.bat' primero
    pause
    exit /b 1
)

echo [LOCAL] Activando entorno virtual...
call venv_smarterp\Scripts\activate.bat

echo [LOCAL] Configurando variables de entorno...
set DJANGO_ENVIRONMENT=development

echo [LOCAL] Iniciando servidor Django...
python manage.py runserver

echo.
echo [SmartERP] Servidor detenido
pause