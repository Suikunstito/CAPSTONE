@echo off
REM ============================================================================
REM SmartERP - Configurar Entorno de Desarrollo
REM ============================================================================
echo [SmartERP] Configurando entorno de desarrollo...

REM Verificar si Python esta disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instalar Python 3.11+ primero.
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv_smarterp" (
    echo [1/4] Creando entorno virtual...
    python -m venv venv_smarterp
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
) else (
    echo [1/4] Entorno virtual ya existe
)

REM Activar entorno e instalar dependencias
echo [2/4] Instalando dependencias base...
call venv_smarterp\Scripts\activate.bat
pip install -r requirements\base.txt
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias base
    pause
    exit /b 1
)

echo [3/4] Instalando dependencias de desarrollo...
pip install -r requirements\development.txt
if errorlevel 1 (
    echo [ERROR] Error instalando dependencias de desarrollo  
    pause
    exit /b 1
)

echo [4/4] Copiando archivo de configuracion...
if not exist ".env.development" (
    copy ".env.example" ".env.development"
)

echo.
echo [SUCCESS] Entorno configurado exitosamente!
echo.
echo Proximo paso: Ejecutar 'dev.bat' para iniciar el servidor
echo.
pause