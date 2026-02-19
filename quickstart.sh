#!/bin/bash
# ============================================================
# SCRIPT DE INICIO RÁPIDO - AURA ESSENCE
# ============================================================
# Ejecutar: bash quickstart.sh

set -e  # Exit on error

clear
echo "╔════════════════════════════════════════════════════════╗"
echo "║  🌟 AURA ESSENCE - MARKETPLACE DE PERFUMERÍA  🌟      ║"
echo "║              Quick Start Script v1.0                   ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# VERIFICACIONES PRE-REQUISITOS
# ============================================================
echo "[1/8] Verificando pre-requisitos..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment no existe"
    echo "    Ejecuta: python3 -m venv .venv"
    exit 1
fi

echo "✓ Python encontrado: $(python --version)"
echo "✓ Virtual environment activo"
echo ""

# ============================================================
# INSTALAR DEPENDENCIAS
# ============================================================
echo "[2/8] Instalando dependencias..."
.venv/bin/pip install -q -r requirements.txt --upgrade
echo "✓ Dependencias actualizadas"
echo ""

# ============================================================
# ANÁLISIS DJANGO
# ============================================================
echo "[3/8] Analizando configuración Django..."
CHECK_RESULT=$(.venv/bin/python manage.py check 2>&1)
if [ $? -eq 0 ]; then
    echo "✓ Configuración válida"
else
    echo "❌ Errores en configuración:"
    echo "$CHECK_RESULT"
    exit 1
fi
echo ""

# ============================================================
# EJECUTAR MIGRACIONES
# ============================================================
echo "[4/8] Ejecutando migraciones..."
.venv/bin/python manage.py migrate --no-input > /dev/null 2>&1
echo "✓ Base de datos actualizada"
echo ""

# ============================================================
# RECOLECTAR STATIC FILES
# ============================================================
echo "[5/8] Recolectando archivos estáticos..."
.venv/bin/python manage.py collectstatic --no-input --clear > /dev/null 2>&1
echo "✓ Archivos estáticos listos"
echo ""

# ============================================================
# CREAR ADMIN Y PRODUCTOS DEMO
# ============================================================
echo "[6/8] Creando cuenta de administrador..."

if [ -z "$ADMIN_USER" ]; then
    ADMIN_USER="admin"
    ADMIN_PASS="AdminPassword123"
    ADMIN_EMAIL="admin@aura-essence.com"
fi

.venv/bin/python manage.py shell << EOF
from django.contrib.auth.models import User

# Crear admin
if not User.objects.filter(username='$ADMIN_USER').exists():
    User.objects.create_superuser(
        username='$ADMIN_USER',
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASS'
    )
    print(f"Created admin user: $ADMIN_USER")
else:
    print(f"Admin user already exists: $ADMIN_USER")
EOF

echo "✓ Admin user listo"
echo "  Usuario: $ADMIN_USER"
echo "  Contraseña: $ADMIN_PASS"
echo ""

# ============================================================
# CREAR PRODUCTOS DEMO
# ============================================================
echo "[7/8] Creando productos de demostración..."

.venv/bin/python manage.py shell << EOF
from apps.api.models import Marca, Categoria, Producto
from decimal import Decimal

# Crear marca
marca, _ = Marca.objects.get_or_create(
    nombre='Aura Essence Exclusive',
    defaults={'descripcion': 'Colección Premium 2026'}
)

# Crear categoría
categoria, _ = Categoria.objects.get_or_create(
    nombre='Eau de Parfum',
    defaults={'slug': 'eau-de-parfum', 'descripcion': 'Alta concentración de aroma'}
)

# Crear productos
productos_demo = [
    {
        'sku': 'AE-001',
        'nombre': 'Essence Floral Midnight',
        'descripcion': 'Notas florales con toques de ámbar oscuro',
        'precio': Decimal('95.99')
    },
    {
        'sku': 'AE-002',
        'nombre': 'Citric Dawn',
        'descripcion': 'Bergamota y neroli frescas para el día',
        'precio': Decimal('75.50')
    },
    {
        'sku': 'AE-003',
        'nombre': 'Oriental Mystique',
        'descripcion': 'Aromas profundos de oud y vainilla',
        'precio': Decimal('120.00')
    },
]

for data in productos_demo:
    if not Producto.objects.filter(sku=data['sku']).exists():
        Producto.objects.create(
            marca=marca,
            categoria=categoria,
            **data
        )
        print(f"Creado: {data['nombre']}")
    else:
        print(f"Ya existe: {data['nombre']}")
EOF

echo "✓ Productos de demostración creados"
echo ""

# ============================================================
# RESUMEN FINAL
# ============================================================
echo "[8/8] Configuración completada"
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              ✓ LISTO PARA INICIAR                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 ACCESO LOCAL:"
echo "   URL Principal:  http://localhost:8000"
echo "   Catálogo:       http://localhost:8000/catalogo/"
echo "   Login:          http://localhost:8000/login/"
echo "   Registro:       http://localhost:8000/registro/"
echo "   Carrito:        http://localhost:8000/carrito/"
echo "   Admin:          http://localhost:8000/admin/"
echo ""
echo "👤 CREDENCIALES ADMIN:"
echo "   Usuario:        $ADMIN_USER"
echo "   Contraseña:     $ADMIN_PASS"
echo ""
echo "📋 PROCESOS:"
echo "   Para iniciar servidor:"
echo "   $ python manage.py runserver"
echo ""
echo "   Para shell interactivo:"
echo "   $ python manage.py shell"
echo ""
echo "   Para crear otro superuser:"
echo "   $ python manage.py createsuperuser"
echo ""
echo "📖 DOCUMENTACIÓN:"
echo "   • DEPLOYMENT_GUIDE.md      → Cómo subir a producción"
echo "   • AUTHENTICATION_GUIDE.md  → Sistema auth + carrito"
echo "   • PROJECT_REPORT.md        → Resumen completo"
echo ""
echo "💡 PRÓXIMOS PASOS:"
echo "   1. Ejecuta: python manage.py runserver"
echo "   2. Visita: http://localhost:8000"
echo "   3. Carga: Admin (http://localhost:8000/admin/)"
echo "   4. Prueba: Registro → Login → Carrito"
echo ""
echo "🚀 ¡Aura Essence está lista!"
echo ""
