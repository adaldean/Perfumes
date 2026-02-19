"""
Ejemplos de prueba para los endpoints de Autenticación y Pagos.

INSTRUCCIONES:
==============
1. Asegúrate de que el servidor Django está corriendo:
   python manage.py runserver

2. Si quieres probar con Stripe:
   - Obtén tus claves de https://dashboard.stripe.com/test/keys
   - Actualiza .env con STRIPE_SECRET_KEY y STRIPE_PUBLIC_KEY
   - Para webhooks, usa Stripe CLI:
     stripe listen --forward-to localhost:8000/api/pago/webhook/

3. Ejecuta este archivo:
   python test_api_examples.py

Nota: Modifica BASE_URL si tu servidor está en otro puerto/dominio.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# ============================================
# Variables Globales para Testing
# ============================================

access_token = None
refresh_token = None
user_id = None
producto_id = 1
pedido_id = None
payment_intent_id = None


# ============================================
# 1. AUTENTICACIÓN
# ============================================

def test_registro():
    """Registrar un nuevo usuario."""
    global user_id
    
    print("\n" + "="*50)
    print("1. REGISTRANDO NUEVO USUARIO")
    print("="*50)
    
    data = {
        "username": "testuser123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPassword123!",
        "password2": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/registro/", json=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        user_id = response.json()['user_id']
        print(f"✅ Usuario registrado con ID: {user_id}")
    else:
        print(f"❌ Error en registro")
        return False
    
    return True


def test_login():
    """Iniciar sesión y obtener tokens JWT."""
    global access_token, refresh_token
    
    print("\n" + "="*50)
    print("2. INICIANDO SESIÓN (LOGIN)")
    print("="*50)
    
    data = {
        "username": "testuser123",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        access_token = result['access']
        refresh_token = result['refresh']
        
        print(f"✅ Login exitoso")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Refresh Token: {refresh_token[:50]}...")
    else:
        print(f"❌ Error en login")
        print(f"Response: {response.json()}")
        return False
    
    return True


def test_refresh_token():
    """Refrescar el access token."""
    global access_token
    
    print("\n" + "="*50)
    print("3. REFRESCANDO ACCESS TOKEN")
    print("="*50)
    
    if not refresh_token:
        print("❌ No hay refresh_token disponible")
        return False
    
    data = {"refresh": refresh_token}
    
    response = requests.post(f"{BASE_URL}/auth/refresh/", json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        access_token = response.json()['access']
        print(f"✅ Token refrescado exitosamente")
        print(f"Nuevo Access Token: {access_token[:50]}...")
    else:
        print(f"❌ Error al refrescar token")
        return False
    
    return True


# ============================================
# 2. PRODUCTOS
# ============================================

def test_listar_productos():
    """Listar productos (sin autenticación requerida)."""
    
    print("\n" + "="*50)
    print("4. LISTANDO PRODUCTOS")
    print("="*50)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/productos/", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Se encontraron {len(products)} productos")
        
        if products:
            print(f"\nPrimer producto:")
            print(json.dumps(products[0], indent=2, ensure_ascii=False))
            return products[0]['id'] if products else None
    else:
        print(f"❌ Error listando productos")
        print(f"Response: {response.json()}")
    
    return None


# ============================================
# 3. PEDIDOS
# ============================================

def test_crear_pedido():
    """Crear un nuevo pedido."""
    global pedido_id
    
    print("\n" + "="*50)
    print("5. CREANDO PEDIDO")
    print("="*50)
    
    if not access_token:
        print("❌ No hay autenticación")
        return False
    
    data = {
        "numero_pedido": "PED-001",
        "estado": "pendiente",
        "total": "99.99",
        "direccion_envio": "Calle Principal 123, Apartamento 4B",
        "telefono": "+34 912 345 678",
        "notas": "Entregar después de las 5 PM"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/pedidos/", json=data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        pedido_id = response.json()['id']
        print(f"✅ Pedido creado con ID: {pedido_id}")
    else:
        print(f"❌ Error creando pedido")
        return False
    
    return True


def test_listar_pedidos():
    """Listar los pedidos del usuario autenticado."""
    
    print("\n" + "="*50)
    print("6. LISTANDO MIS PEDIDOS")
    print("="*50)
    
    if not access_token:
        print("❌ No hay autenticación")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/pedidos/", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        pedidos = response.json()
        print(f"✅ Se encontraron {len(pedidos)} pedidos")
        
        if pedidos:
            print(f"\nPrimer pedido:")
            print(json.dumps(pedidos[0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error listando pedidos")
        print(f"Response: {response.json()}")
    
    return True


# ============================================
# 4. PAGOS (STRIPE)
# ============================================

def test_crear_payment_intent():
    """Crear un PaymentIntent en Stripe."""
    global payment_intent_id
    
    print("\n" + "="*50)
    print("7. CREANDO PAYMENT INTENT (STRIPE)")
    print("="*50)
    
    if not access_token or not pedido_id:
        print("❌ Se necesita estar autenticado y tener un pedido")
        return False
    
    data = {
        "pedido_id": pedido_id,
        "email": "testuser@example.com",
        "nombre": "Test User"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/pago/crear/", json=data, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        payment_intent_id = response.json()['payment_intent_id']
        client_secret = response.json()['client_secret']
        
        print(f"\n✅ PaymentIntent creado exitosamente")
        print(f"PaymentIntent ID: {payment_intent_id}")
        print(f"Client Secret: {client_secret}")
        print(f"\nÚsalo en tu frontend con Stripe.js:")
        print(f"stripe.confirmCardPayment('{client_secret}', {{...}})")
        
    else:
        print(f"❌ Error creando PaymentIntent")
        return False
    
    return True


def test_verificar_pago():
    """Verificar el estado de un pago."""
    
    print("\n" + "="*50)
    print("8. VERIFICANDO ESTADO DE PAGO")
    print("="*50)
    
    if not payment_intent_id:
        print("❌ No hay PaymentIntent disponible")
        return False
    
    response = requests.get(f"{BASE_URL}/pago/verificar/{payment_intent_id}/")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print(f"✅ Estado del pago verificado")
    else:
        print(f"❌ Error verificando pago")
    
    return True


def test_listar_pagos():
    """Listar los pagos del usuario autenticado."""
    
    print("\n" + "="*50)
    print("9. LISTANDO MIS PAGOS")
    print("="*50)
    
    if not access_token:
        print("❌ No hay autenticación")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/pago/", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        pagos = response.json()
        print(f"✅ Se encontraron {len(pagos)} pagos")
        
        if pagos:
            print(f"\nPrimer pago:")
            print(json.dumps(pagos[0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error listando pagos")
        print(f"Response: {response.json()}")
    
    return True


# ============================================
# MAIN - Ejecutar todas las pruebas
# ============================================

def main():
    """Ejecutar todas las pruebas en orden."""
    
    print("\n" + "="*50)
    print("🧪 TESTING DE API - AUTENTICACIÓN Y PAGOS")
    print("="*50)
    
    # Autenticación
    if not test_registro():
        return
    
    if not test_login():
        return
    
    if not test_refresh_token():
        return
    
    # Productos
    test_listar_productos()
    
    # Pedidos
    if not test_crear_pedido():
        return
    
    test_listar_pedidos()
    
    # Pagos
    if not test_crear_payment_intent():
        return
    
    test_verificar_pago()
    test_listar_pagos()
    
    print("\n" + "="*50)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("="*50)
    print("\n📝 Próximos pasos:")
    print("1. El cliente_secret se usa en Stripe.js en el frontend")
    print("2. Configura el webhook de Stripe para recibir notificaciones")
    print("3. Prueba con tarjetas de prueba: 4242 4242 4242 4242")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error durante testing: {str(e)}")
        import traceback
        traceback.print_exc()
