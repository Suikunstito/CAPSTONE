@echo off
REM SmartERP - Crear Superusuario
REM Facilita la creación de usuario administrador

echo ========================================
echo SmartERP - Crear Superusuario
echo ========================================
echo.

REM Verificar que existe el entorno virtual
if not exist "venv_smarterp\Scripts\activate.bat" (
    echo [ERROR] Entorno virtual no encontrado
    echo Ejecuta primero: setup-dev.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/2] Activando entorno virtual...
call venv_smarterp\Scripts\activate.bat

REM Crear superusuario
echo.
echo [2/2] Creando superusuario de Django...
echo.
python manage.py createsuperuser

echo.
echo ========================================
echo Superusuario creado exitosamente
echo ========================================
echo.
echo Ahora puedes:
echo   - Iniciar servidor: dev.bat
echo   - Acceder a /admin/ con tus credenciales
echo.
pause
