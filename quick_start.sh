#!/bin/bash
# ============================================
# QUICK START - AUTENTICACIÓN Y PAGOS
# ============================================
# 
# Este script configura rápidamente tu proyecto
# con autenticación JWT y pagos Stripe
#
# Uso: bash quick_start.sh
#

set -e

echo ""
echo "=========================================="
echo "🚀 CONFIGURACIÓN RÁPIDA - STRIPE + JWT"
echo "=========================================="
echo ""

# 1. Instalar dependencias
echo "1️⃣  Instalando dependencias..."
pip install -r requirements.txt

echo "✅ Dependencias instaladas"
echo ""

# 2. Ejecutar migraciones
echo "2️⃣  Ejecutando migraciones..."
python manage.py migrate

echo "✅ Migraciones completadas"
echo ""

# 3. Crear superusuario (opcional)
echo "3️⃣  ¿Crear superusuario para admin? (s/n)"
read -r response
if [[ $response == "s" || $response == "S" ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "=========================================="
echo "⚙️  CONFIGURACIÓN DE STRIPE"
echo "=========================================="
echo ""
echo "Necesitas tu clave de Stripe PUBLIC para el formulario de pago:"
echo "1. Ve a https://dashboard.stripe.com/test/keys"
echo "2. Copia tu 'Publishable key' (pk_test_...)"
echo "3. Reemplaza 'YOUR_PUBLISHABLE_KEY' en payment_form_example.html"
echo ""
echo "Para webhooks locales:"
echo "1. Instala Stripe CLI: https://stripe.com/docs/stripe-cli"
echo "2. Ejecuta: stripe listen --forward-to localhost:8000/api/pago/webhook/"
echo "3. Copia el 'Signing secret' a .env como STRIPE_WEBHOOK_SECRET"
echo ""

# Crear .env si no existe
if [ ! -f .env ]; then
    echo "4️⃣  Creando archivo .env..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita .env y agrega tus claves de Stripe"
else
    echo "ℹ️  .env ya existe"
fi

echo ""
echo "=========================================="
echo "✅ SETUP COMPLETADO"
echo "=========================================="
echo ""
echo "📖 PRÓXIMOS PASOS:"
echo ""
echo "1️⃣  Edita .env y agrega:"
echo "   STRIPE_SECRET_KEY=sk_test_..."
echo "   STRIPE_PUBLIC_KEY=pk_test_..."
echo "   STRIPE_WEBHOOK_SECRET=whsec_test_..."
echo ""
echo "2️⃣  Inicia el servidor:"
echo "   python manage.py runserver"
echo ""
echo "3️⃣  Prueba los endpoints:"
echo "   python test_api_examples.py"
echo ""
echo "4️⃣  Lee la documentación:"
echo "   - AUTHENTICATION_PAYMENTS.md (completa)"
echo "   - SETUP_CHANGES.md (resumen de cambios)"
echo "   - payment_form_example.html (formulario de pago)"
echo ""
echo "5️⃣  Endpoints disponibles:"
echo "   POST   /api/auth/registro/"
echo "   POST   /api/auth/login/"
echo "   POST   /api/auth/refresh/"
echo "   GET    /api/productos/"
echo "   POST   /api/pedidos/"
echo "   POST   /api/pago/crear/"
echo "   GET    /api/pago/verificar/{id}/"
echo ""
echo "¡Bienvenido! 🎉"
echo ""
