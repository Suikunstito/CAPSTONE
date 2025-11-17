@echo off
REM ============================================================================
REM SmartERP - Limpiar Entorno
REM ============================================================================
echo [SmartERP] Limpiando entorno...

echo [1/4] Deteniendo contenedores Docker...
docker-compose down >nul 2>&1

echo [2/4] Eliminando entorno virtual...
if exist "venv_smarterp" (
    rmdir /s /q "venv_smarterp"
    echo [OK] Entorno virtual eliminado
) else (
    echo [OK] Entorno virtual no existia
)

echo [3/4] Limpiando archivos temporales...
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
for /d /r . %%d in (*.egg-info) do @if exist "%%d" rmdir /s /q "%%d" >nul 2>&1

echo [4/4] Limpiando logs...
if exist "*.log" del "*.log" >nul 2>&1

echo.
echo [SUCCESS] Entorno limpiado completamente
echo [INFO] Para empezar de nuevo: ejecutar 'setup-dev.bat'
echo.
pause