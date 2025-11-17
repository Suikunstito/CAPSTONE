@echo off
REM SmartERP - Quick Setup sin Docker
REM Usar cuando Docker no está disponible o no se quiere instalar

echo.
echo [92m======================================[0m
echo [92m    SmartERP - Setup Rápido Local[0m
echo [92m======================================[0m
echo.

REM Verificar si Task está disponible
task --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [92m✅ Task encontrado, usando configuración automática...[0m
    echo.
    task setup-dev:local
) else (
    echo [93m⚠️  Task no encontrado, usando setup manual...[0m
    echo.
    
    REM Setup manual sin Task
    echo [96mVerificando Python...[0m
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [91m❌ Python no encontrado[0m
        echo [93m💡 Instalar Python desde: https://python.org[0m
        pause
        exit /b 1
    )
    echo [92m✅ Python encontrado[0m
    
    echo.
    echo [96mCreando entorno virtual...[0m
    if exist venv_smarterp (
        echo [93m⚠️  Entorno virtual ya existe, recreando...[0m
        rmdir /s /q venv_smarterp
    )
    python -m venv venv_smarterp
    
    echo.
    echo [96mInstalando dependencias...[0m
    call venv_smarterp\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements\development.txt
    
    echo.
    echo [96mConfigurando ambiente...[0m
    if not exist .env.development (
        copy .env.example .env.development >nul
    )
    
    echo.
    echo [96mVerificando configuración...[0m
    python manage.py check
    
    echo.
    echo [92m======================================[0m
    echo [92m  Setup Local Completado![0m
    echo [92m======================================[0m
    echo.
    echo Para ejecutar SmartERP:
    if %errorlevel% equ 0 (
        echo   [96mtask dev:local[0m    (si tienes Task)
    )
    echo   [96mvenv_smarterp\Scripts\activate.bat[0m
    echo   [96mpython manage.py runserver[0m
    echo.
    echo Para instalar Task (recomendado):
    echo   [96mchoco install go-task[0m
    echo   o descargar desde: [96mhttps://taskfile.dev[0m
)

echo.
pause