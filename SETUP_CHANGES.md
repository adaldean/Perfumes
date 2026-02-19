# 🚀 Implementación de Autenticación JWT y Pagos con Stripe

## 📝 Resumen de Cambios

Se han implementado exitosamente en el proyecto Django:

### ✅ 1. **Autenticación con JWT (JSON Web Tokens)**
- Endpoints de registro y login seguros
- Tokens de acceso y refresh automáticos
- Autenticación en todos los endpoints de la API

### ✅ 2. **Sistema de Pagos con Stripe**
- Creación de PaymentIntents
- Webhooks para actualizar estados de pago
- Integración completa con Stripe API

### ✅ 3. **Modelos de Base de Datos**
- `Pedido` - Gestión de pedidos de clientes
- `DetallePedido` - Detalles de cada pedido
- `Pago` - Registro de transacciones de Stripe

---

## 📦 Dependencias Instaladas

```bash
djangorestframework-simplejwt==5.3.2  # Autenticación JWT
stripe==7.4.0                         # SDK de Stripe
requests==2.31.0                      # HTTP requests
```

---

## 📂 Archivos Modificados y Creados

### Modificados:
- **[myproject/settings.py](myproject/settings.py)** - Configuración de JWT y Stripe
- **requirements.txt** - Nuevas dependencias
- **apps/api/models.py** - Nuevos modelos (Pedido, DetallePedido, Pago)
- **apps/api/serializers.py** - Serializadores para autenticación y pagos
- **apps/api/views.py** - Nuevas vistas para autenticación y pagos
- **apps/api/urls.py** - Nuevas rutas de API
- **apps/api/admin.py** - Interfaz de administración para nuevos modelos
- **.env.example** - Variables de entorno para Stripe

### Creados:
- **[apps/api/payments.py](apps/api/payments.py)** - Módulo de integración con Stripe
- **[AUTHENTICATION_PAYMENTS.md](AUTHENTICATION_PAYMENTS.md)** - Documentación completa (📖 LEER ESTO)
- **[test_api_examples.py](test_api_examples.py)** - Script de testing
- **[payment_form_example.html](payment_form_example.html)** - Ejemplo de formulario de pago

---

## 🔧 Configuración Rápida

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env y agrega tus claves de Stripe:
# STRIPE_SECRET_KEY=sk_test_...
# STRIPE_PUBLIC_KEY=pk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_test_...
```

Obtén tus claves en: https://dashboard.stripe.com/test/keys

### 3. Ejecutar Migraciones
```bash
python manage.py migrate
```

### 4. Iniciar Servidor
```bash
python manage.py runserver
```

---

## 🔐 Autenticación JWT

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/registro/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Obtener tokens (access + refresh) |
| POST | `/api/auth/refresh/` | Refrescar access token |

### Ejemplo de Uso

**1. Registrar Usuario:**
```bash
curl -X POST http://localhost:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_perez",
    "email": "juan@example.com",
    "password": "Contraseña123!",
    "password2": "Contraseña123!"
  }'
```

**2. Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan_perez",
    "password": "Contraseña123!"
  }'
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**3. Usar Token en Peticiones:**
```bash
curl -X GET http://localhost:8000/api/productos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 💳 Pagos con Stripe

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/pago/crear/` | Crear PaymentIntent |
| GET | `/api/pago/verificar/{id}/` | Verificar estado de pago |
| POST | `/api/pago/webhook/` | Webhook de Stripe (automático) |

### Flujo de Pago

```
1. Cliente crea un Pedido
   POST /api/pedidos/

2. Cliente solicita PaymentIntent
   POST /api/pago/crear/ 
   Body: {"pedido_id": 1, "email": "...", "nombre": "..."}
   
3. Frontend recibe client_secret
   Usa Stripe.js para confirmar el pago
   
4. Stripe envía webhook al servidor
   POST /api/pago/webhook/
   Actualiza estado de Pago y Pedido en BD
```

### Configurar Webhook

1. Ve a https://dashboard.stripe.com/test/webhooks
2. Crea nuevo endpoint:
   - **URL:** `https://tu-dominio.com/api/pago/webhook/`
   - **Eventos:** 
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
3. Copia el **Signing Secret** a `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_test_...
   ```

### Testing Local con Stripe CLI

```bash
# 1. Instalar Stripe CLI
brew install stripe/stripe-cli/stripe  # macOS

# 2. Autenticarse
stripe login

# 3. En otra terminal, escuchar webhooks
stripe listen --forward-to localhost:8000/api/pago/webhook/

# 4. Copiar el signing secret a .env
# STRIPE_WEBHOOK_SECRET=whsec_...

# 5. Simular un pago
stripe trigger payment_intent.succeeded
```

---

## 🧪 Testing

### Ejecutar Script de Testing
```bash
python test_api_examples.py
```

Este script prueba:
✅ Registro de usuario
✅ Login y obtención de tokens
✅ Refresco de token
✅ Listado de productos
✅ Crear y listar pedidos
✅ Crear PaymentIntent
✅ Verificar estado de pago

### Tarjetas de Prueba de Stripe

| Número | Resultado | CVC | Fecha |
|--------|-----------|-----|-------|
| `4242 4242 4242 4242` | ✅ Exitoso | Cualquier | Futura |
| `4000 0000 0000 0002` | ❌ Rechazado | Cualquier | Futura |
| `4000 0025 0000 3155` | ⚠️ 3D Secure | Cualquier | Futura |

---

## 📖 Documentación Completa

Para documentación detallada, ejemplos y solución de problemas, ver:
👉 **[AUTHENTICATION_PAYMENTS.md](AUTHENTICATION_PAYMENTS.md)**

Contiene:
- Guía completa de autenticación JWT
- Sistema de pagos paso a paso
- Ejemplos de código en JavaScript y cURL
- Testing con Stripe CLI
- Solución de problemas

---

## 📊 Base de Datos

### Nuevas Tablas Creadas

1. **pedidos** - Pedidos de clientes
2. **detalles_pedidos** - Items de cada pedido
3. **pagos** - Transacciones de Stripe

### Ver en Admin

```
http://localhost:8000/admin/
```

Acceso a:
- Pedidos
- Detalles de Pedidos
- Pagos
- Usuarios

---

## 🔒 Seguridad

✅ JWT con 24h de expiración
✅ Refresh tokens con 7 días
✅ Verificación de firma de webhooks
✅ CORS configurado
✅ Contraseñas hasheadas

---

## 🚀 Próximos Pasos

1. **Obtener claves de Stripe reales** (producción)
2. **Configurar webhook en Stripe Dashboard**
3. **Integrar formulario de pago en frontend** (ver payment_form_example.html)
4. **Implementar lógica de correos** (opcional)
5. **Hacer deploy en producción**

---

## ❓ Preguntas Frecuentes

**P: ¿Dónde pongo mi sk_test_?**
R: En el archivo `.env` en la raíz del proyecto: `STRIPE_SECRET_KEY=sk_test_...`

**P: ¿El webhook no funciona localmente?**
R: Usa Stripe CLI: `stripe listen --forward-to localhost:8000/api/pago/webhook/`

**P: ¿Cómo testing sin Stripe CLI?**
R: Usa el script `test_api_examples.py` pero sin la parte de webhook

**P: ¿Qué pasa si el pago falla?**
R: El estado pasa a "fallido" y se guarda la razón en `razon_fallo`

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación en [AUTHENTICATION_PAYMENTS.md](AUTHENTICATION_PAYMENTS.md)
2. Verifica `.env` tiene todas las variables
3. Ejecuta `python manage.py check`
4. Revisa los logs de Django

---

**Última actualización:** Febrero 2026
