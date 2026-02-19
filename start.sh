#!/bin/bash

# Script para iniciar el desarrollo en Django
# Uso: bash start.sh

echo "🚀 Iniciando servidor Django..."
echo ""

# Activar entorno virtual
source .venv/bin/activate

# Mensaje de bienvenida
echo "✅ Entorno virtual activado"
echo ""
echo "📝 Información del servidor:"
echo "   URL: http://127.0.0.1:8000"
echo "   Admin: http://127.0.0.1:8000/admin"
echo "   API: http://127.0.0.1:8000/api"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""

# Iniciar servidor
python manage.py runserver
