# 🔐 Autenticación y 💳 Pagos con Stripe - Guía de Implementación

Este documento explica cómo usar los nuevos sistemas de autenticación JWT y pagos con Stripe integrados en tu API Django.

---

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Autenticación con JWT](#autenticación-con-jwt)
3. [Sistema de Pagos con Stripe](#sistema-de-pagos-con-stripe)
4. [Endpoints de la API](#endpoints-de-la-api)
5. [Testing y Pruebas](#testing-y-pruebas)

---

## ⚙️ Configuración Inicial

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las nuevas dependencias incluyen:
- `djangorestframework-simplejwt` - Autenticación JWT
- `stripe` - SDK de Stripe
- `requests` - HTTP requests

### 2. Configurar Variables de Entorno

Copia `.env.example` a `.env` y completa:

```bash
cp .env.example .env
```

**Archivo `.env`:**
```env
# Configuración de Stripe (TEST)
STRIPE_PUBLIC_KEY=pk_test_YOUR_PUBLIC_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET_HERE
```

### 3. Obtener Claves de Stripe

1. Ve a [Stripe Dashboard](https://dashboard.stripe.com)
2. Asegúrate de estar en modo **TEST**
3. Copia las claves de prueba:
   - **Public Key**: `pk_test_...`
   - **Secret Key**: `sk_test_...`

### 4. Crear Migraciones y Ejecutarlas

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

### 6. Iniciar el Servidor

```bash
python manage.py runserver
```

---

## 🔐 Autenticación con JWT

### ¿Qué es JWT?

JWT (JSON Web Token) es un estándar seguro para autenticación sin sesiones. Los tokens expiran automáticamente.

- **Access Token**: Dura 24 horas, se usa para acceder a la API
- **Refresh Token**: Dura 7 días, se usa para obtener un nuevo Access Token

### Endpoints de Autenticación

#### 1. Registrar un Nuevo Usuario

**POST** `/api/auth/registro/`

```json
{
  "username": "juan_perez",
  "email": "juan@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "password": "contraseña123!",
  "password2": "contraseña123!"
}
```

**Respuesta (201):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user_id": 1,
  "username": "juan_perez",
  "email": "juan@example.com"
}
```

#### 2. Iniciar Sesión (Obtener Tokens)

**POST** `/api/auth/login/`

```json
{
  "username": "juan_perez",
  "password": "contraseña123!"
}
```

**Respuesta (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. Refrescar Access Token

**POST** `/api/auth/refresh/`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Respuesta (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar el Token en Peticiones

Agregar el header `Authorization` en todas las peticiones autenticadas:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/productos/
```

Ejemplo con JavaScript/Fetch:
```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/pedidos/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 💳 Sistema de Pagos con Stripe

### ¿Cómo Funciona?

1. **Cliente crea un pedido** → Se guarda en BD
2. **Cliente solicita crear pago** → Se crea PaymentIntent en Stripe
3. **Cliente completa el pago** → Stripe envía webhook a tu servidor
4. **Servidor actualiza BD** → El estado del pedido cambia a "procesando"

### Flujo Completo de Pago

```
┌─────────────────────┐
│  Cliente crea       │
│  Pedido en BD       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  POST /api/pago/crear/          │
│  Recibe: pedido_id, email, nombre
│  Retorna: client_secret         │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Cliente usa        │
│  client_secret en   │
│  Stripe.js          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Cliente completa   │
│  pago en Stripe     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Webhook de Stripe llega a      │
│  POST /api/pago/webhook/        │
│  Actualiza estado de Pago y     │
│  Pedido en BD                   │
└─────────────────────────────────┘
```

### Endpoints de Pagos

#### 1. Crear PaymentIntent

**POST** `/api/pago/crear/`

**Headers requeridos:**
```
Authorization: Bearer {ACCESS_TOKEN}
```

**Body:**
```json
{
  "pedido_id": 1,
  "email": "cliente@example.com",
  "nombre": "Juan Pérez"
}
```

**Respuesta (200):**
```json
{
  "client_secret": "pi_XXXXX_secret_XXXXX",
  "payment_intent_id": "pi_XXXXX",
  "monto": 99.99,
  "numero_pedido": "PED-001"
}
```

**Usar en Frontend (JavaScript):**
```javascript
// 1. Obtener el client_secret del backend
const response = await fetch('/api/pago/crear/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    pedido_id: 1,
    email: 'cliente@example.com',
    nombre: 'Juan Pérez'
  })
});

const { client_secret } = await response.json();

// 2. Usar Stripe.js para completar el pago
const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
  payment_method: {
    card: cardElement,
    billing_details: { name: 'Juan Pérez' }
  }
});

if (paymentIntent && paymentIntent.status === 'succeeded') {
  console.log('¡Pago exitoso!');
}
```

#### 2. Verificar Estado de un Pago

**GET** `/api/pago/verificar/{payment_intent_id}/`

**Respuesta (200):**
```json
{
  "status": "succeeded",
  "monto": 99.99,
  "moneda": "USD",
  "estado_local": "exitoso"
}
```

#### 3. Webhook de Stripe

**POST** `/api/pago/webhook/`

Este endpoint es **automático** - Stripe lo llama cuando:
- ✅ Un pago se completa exitosamente
- ❌ Un pago falla

**Configuración en Stripe Dashboard:**
1. Ve a [Webhooks](https://dashboard.stripe.com/test/webhooks)
2. Crea nuevo endpoint:
   - URL: `http://tu-dominio.com/api/pago/webhook/`
   - Eventos: 
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
3. Copia el "Signing secret" a `STRIPE_WEBHOOK_SECRET` en `.env`

---

## 📡 Endpoints de la API

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/registro/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Iniciar sesión (obtener tokens) |
| POST | `/api/auth/refresh/` | Refrescar access token |

### Productos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos/` | Listar productos |
| GET | `/api/productos/{id}/` | Obtener producto |
| POST | `/api/productos/` | Crear producto (admin) |
| PUT | `/api/productos/{id}/` | Actualizar producto (admin) |
| DELETE | `/api/productos/{id}/` | Eliminar producto (admin) |

### Pedidos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/pedidos/` | Ver mis pedidos |
| GET | `/api/pedidos/{id}/` | Ver detalle de pedido |
| POST | `/api/pedidos/` | Crear pedido |

### Pagos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/pago/crear/` | Crear PaymentIntent |
| GET | `/api/pago/verificar/{id}/` | Verificar estado de pago |
| POST | `/api/pago/webhook/` | Webhook de Stripe |

---

## 🧪 Testing y Pruebas

### Tarjetas de Prueba de Stripe

Usa estas tarjetas en modo TEST para simular diferentes escenarios:

| Número | Resultado | CVC | Fecha |
|--------|-----------|-----|-------|
| `4242 4242 4242 4242` | ✅ Exitoso | Cualquier 3 dígitos | Futura |
| `4000 0000 0000 0002` | ❌ Rechazado | Cualquier 3 dígitos | Futura |
| `4000 0025 0000 3155` | ⚠️ Requiere 3D Secure | Cualquier 3 dígitos | Futura |

### Testing con Webhook Localmente

1. **Instalar Stripe CLI**
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe
   
   # Linux
   wget https://github.com/stripe/stripe-cli/releases/download/v1.x.x/stripe_linux_x86_64.zip
   unzip stripe_linux_x86_64.zip
   sudo mv stripe /usr/local/bin
   ```

2. **Autenticarse con Stripe**
   ```bash
   stripe login
   ```

3. **Escuchar eventos en otra terminal**
   ```bash
   stripe listen --forward-to localhost:8000/api/pago/webhook/
   ```

4. **Copiar el signing secret a `.env`**
   ```
   STRIPE_WEBHOOK_SECRET=whsec_test_...
   ```

5. **Realizar una transacción de prueba**
   ```bash
   stripe trigger payment_intent.succeeded
   ```

### Ejemplo de Testing con cURL

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# 3. Usar el access token en siguientes peticiones
TOKEN="YOUR_ACCESS_TOKEN_HERE"
curl -X GET http://localhost:8000/api/productos/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📚 Recursos Adicionales

- [Documentación de Stripe](https://stripe.com/docs)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Django REST Framework JWT](https://github.com/jpadilla/django-rest-framework-simplejwt)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

## 🆘 Solución de Problemas

### Error: `STRIPE_SECRET_KEY not configured`
✅ Asegúrate de que `.env` existe y está en la raíz del proyecto

### Error: `Invalid webhook signature`
✅ Verifica que `STRIPE_WEBHOOK_SECRET` sea correcto en `.env`

### Error: `Pedido no encontrado`
✅ Verifica que el `pedido_id` existe en la BD y pertenece al usuario

### Token JWT expirado
✅ Usa el `refresh_token` para obtener un nuevo `access_token`

---

**Última actualización:** Febrero 2026
