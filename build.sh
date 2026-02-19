#!/bin/bash
# Script de build para Render

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input --clear

# Ejecutar migraciones
python manage.py migrate
