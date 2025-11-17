#!/bin/bash

# SmartERP - Quick Setup sin Docker
# Usar cuando Docker no está disponible o no se quiere instalar

echo ""
echo -e "\033[92m======================================\033[0m"
echo -e "\033[92m    SmartERP - Setup Rápido Local\033[0m"
echo -e "\033[92m======================================\033[0m"
echo ""

# Verificar si Task está disponible
if command -v task >/dev/null 2>&1; then
    echo -e "\033[92m✅ Task encontrado, usando configuración automática...\033[0m"
    echo ""
    task setup-dev:local
else
    echo -e "\033[93m⚠️  Task no encontrado, usando setup manual...\033[0m"
    echo ""
    
    # Setup manual sin Task
    echo -e "\033[96mVerificando Python...\033[0m"
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "\033[91m❌ Python no encontrado\033[0m"
        echo -e "\033[93m💡 Instalar Python desde: https://python.org\033[0m"
        exit 1
    fi
    echo -e "\033[92m✅ Python encontrado\033[0m"
    
    echo ""
    echo -e "\033[96mCreando entorno virtual...\033[0m"
    if [ -d "venv_smarterp" ]; then
        echo -e "\033[93m⚠️  Entorno virtual ya existe, recreando...\033[0m"
        rm -rf venv_smarterp
    fi
    python3 -m venv venv_smarterp
    
    echo ""
    echo -e "\033[96mInstalando dependencias...\033[0m"
    source venv_smarterp/bin/activate
    pip install --upgrade pip
    pip install -r requirements/development.txt
    
    echo ""
    echo -e "\033[96mConfigurando ambiente...\033[0m"
    if [ ! -f ".env.development" ]; then
        cp .env.example .env.development
    fi
    
    echo ""
    echo -e "\033[96mVerificando configuración...\033[0m"
    python manage.py check
    
    echo ""
    echo -e "\033[92m======================================\033[0m"
    echo -e "\033[92m  Setup Local Completado!\033[0m"
    echo -e "\033[92m======================================\033[0m"
    echo ""
    echo "Para ejecutar SmartERP:"
    if command -v task >/dev/null 2>&1; then
        echo -e "  \033[96mtask dev:local\033[0m    (si tienes Task)"
    fi
    echo -e "  \033[96msource venv_smarterp/bin/activate\033[0m"
    echo -e "  \033[96mpython manage.py runserver\033[0m"
    echo ""
    echo "Para instalar Task (recomendado):"
    echo -e "  \033[96msh -c \"\$(curl --location https://taskfile.dev/install.sh)\" -- -d -b /usr/local/bin\033[0m"
fi

echo ""
read -p "Presionar Enter para continuar..."