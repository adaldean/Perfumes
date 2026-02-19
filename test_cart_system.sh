"""
Script de prueba para el sistema de autenticación y carrito.
Ejecuta: python manage.py shell < test_auth_cart.py
"""

from django.contrib.auth.models import User
from apps.api.models import Producto, Carrito, ItemCarrito
from decimal import Decimal

print("\n" + "="*60)
print("PRUEBA DEL SISTEMA DE AUTENTICACIÓN Y CARRITO")
print("="*60)

# ============================================================
# TEST 1: Crear Usuario y Carrito
# ============================================================
print("\n[TEST 1] Creando usuario de prueba...")

user, created = User.objects.get_or_create(
    username='clienteprueba',
    defaults={
        'email': 'cliente@prueba.com',
        'first_name': 'Cliente',
        'last_name': 'Prueba'
    }
)

if created:
    user.set_password('TestPassword123')
    user.save()
    print(f"✓ Usuario creado: {user.username}")
else:
    print(f"✓ Usuario existente: {user.username}")

# Crear carrito
carrito, created = Carrito.objects.get_or_create(usuario=user)
print(f"✓ Carrito {'creado' if created else 'existente'} - ID: {carrito.id}")

# ============================================================
# TEST 2: Crear Productos de Prueba
# ============================================================
print("\n[TEST 2] Creando productos de prueba...")

productos_data = [
    {
        'nombre': 'Eau de Parfum Floral',
        'descripcion': 'Aroma floral sofisticado',
        'precio': Decimal('89.99'),
        'sku': 'PERFUME-001'
    },
    {
        'nombre': 'Eau de Toilette Cítrica',
        'descripcion': 'Notas cítricas frescas',
        'precio': Decimal('65.50'),
        'sku': 'PERFUME-002'
    },
    {
        'nombre': 'Colonia Premium Oriental',
        'descripcion': 'Aromas orientales profundos',
        'precio': Decimal('120.00'),
        'sku': 'PERFUME-003'
    }
]

productos = []
for data in productos_data:
    producto, created = Producto.objects.get_or_create(
        sku=data['sku'],
        defaults=data
    )
    productos.append(producto)
    status = "creado" if created else "existente"
    print(f"✓ {producto.nombre} ({status}) - ${producto.precio}")

# ============================================================
# TEST 3: Agregar Items al Carrito
# ============================================================
print("\n[TEST 3] Agregando productos al carrito...")

items_data = [
    (productos[0], 2),  # 2 x Eau de Parfum Floral
    (productos[1], 1),  # 1 x Eau de Toilette Cítrica
]

for producto, cantidad in items_data:
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    if not created:
        item.cantidad += cantidad
        item.save()
    
    print(f"✓ {producto.nombre} x{item.cantidad} = ${item.subtotal}")

# ============================================================
# TEST 4: Calcular Totales
# ============================================================
print("\n[TEST 4] Calculando totales del carrito...")

print(f"\nCarrito de: {user.first_name} {user.last_name}")
print("-" * 60)

for item in carrito.items.all():
    print(f"  {item.producto.nombre:40} ${item.producto.precio:8.2f} x {item.cantidad:2} = ${item.subtotal:8.2f}")

print("-" * 60)
subtotal = carrito.total
shipping = Decimal('15.00')
tax = subtotal * Decimal('0.16')
total = subtotal + shipping + tax

print(f"  Subtotal:     ${subtotal:.2f}")
print(f"  Envío:        ${shipping:.2f}")
print(f"  IVA (16%):    ${tax:.2f}")
print(f"  TOTAL:        ${total:.2f}")
print("-" * 60)

# ============================================================
# TEST 5: Actualizar Cantidad
# ============================================================
print("\n[TEST 5] Actualizando cantidad de un producto...")

item_to_update = carrito.items.first()
old_qty = item_to_update.cantidad
item_to_update.cantidad = 5
item_to_update.save()

print(f"✓ {item_to_update.producto.nombre}: {old_qty} → {item_to_update.cantidad} unidades")
print(f"  Nuevo subtotal: ${item_to_update.subtotal:.2f}")

# ============================================================
# TEST 6: Eliminar Item
# ============================================================
print("\n[TEST 6] Eliminando un producto del carrito...")

if carrito.items.count() > 1:
    item_to_delete = carrito.items.last()
    producto_nombre = item_to_delete.producto.nombre
    item_to_delete.delete()
    print(f"✓ {producto_nombre} eliminado del carrito")
    print(f"  Items restantes: {carrito.items.count()}")

# ============================================================
# TEST 7: Info Resumen
# ============================================================
print("\n[TEST 7] Información del Carrito")
print(f"  Total de items: {carrito.cantidad_items}")
print(f"  Cantidad diferente de productos: {carrito.items.count()}")
print(f"  Subtotal: ${carrito.total:.2f}")

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "="*60)
print("✓ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
print("="*60)
print("\nPróximos pasos:")
print("1. Visitar http://localhost:8000/registro/ para nuevo usuario")
print("2. Visitar http://localhost:8000/login/ para iniciar sesión")
print("3. Visitar http://localhost:8000/catalogo/ para ver productos")
print("4. Visitar http://localhost:8000/carrito/ para ver carrito")
print("\n")
