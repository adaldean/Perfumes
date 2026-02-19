# 💳 ROADMAP FASE 3: INTEGRACIÓN STRIPE

## 📌 Estado Actual

✅ Autenticación completa
✅ Carrito persistente operativo
⏳ **PAGOS**: Infraestructura lista, UI pendiente

---

## 🎯 Lo que Falta (3 pasos principales)

### PASO 1: Frontend - Formulario de Pago (Stripe Elements)
### PASO 2: Backend - Crear orden desde carrito
### PASO 3: Confirmación - Email + Redirect

---

## 📋 PASO 1: CREAR checkout.html (Frontend Stripe)

```html
<!-- templates/checkout.html -->

{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>Checkout | Aura Essence</title>
    <link rel="stylesheet" href="{% static 'css/index.css' %}">
    <script src="https://js.stripe.com/v3/"></script>
</head>
<body>
{% if user.is_authenticated %}

<div class="checkout-container">
    <h1>Finalizar Compra</h1>
    
    <!-- RESUMEN PEDIDO -->
    <div class="order-summary">
        <h2>Resumen del Pedido</h2>
        <table>
            <tr>
                <td>Subtotal</td>
                <td>${{ carrito.total|floatformat:2 }}</td>
            </tr>
            <tr>
                <td>Envío</td>
                <td>$15.00</td>
            </tr>
            <tr>
                <td>IVA (16%)</td>
                <td>${{ impuestos|floatformat:2 }}</td>
            </tr>
            <tr class="total-row">
                <td>TOTAL</td>
                <td>${{ total_final|floatformat:2 }}</td>
            </tr>
        </table>
    </div>
    
    <!-- FORMULARIO STRIPE -->
    <form id="payment-form" method="POST" action="{% url 'api:crear_pago' %}">
        {% csrf_token %}
        
        <!-- INFORMACIÓN DE ENVÍO -->
        <fieldset>
            <legend>Información de Envío</legend>
            <input type="text" name="nombre" placeholder="Nombre completo" required>
            <input type="email" name="email" placeholder="Email" value="{{ user.email }}" required>
            <input type="tel" name="telefono" placeholder="Teléfono" required>
            <textarea name="direccion" placeholder="Dirección completa" required></textarea>
        </fieldset>
        
        <!-- FORMULARIO STRIPE ELEMENTS -->
        <fieldset>
            <legend>Información de Pago</legend>
            <div id="card-element"></div>
            <div id="card-errors" role="alert"></div>
        </fieldset>
        
        <button type="submit" id="submit-button" class="cta-button">
            Pagar ${{ total_final|floatformat:2 }}
        </button>
    </form>
</div>

<!-- JavaScript para Stripe -->
<script>
const stripe = Stripe('{{ stripe_public_key }}');
const elements = stripe.elements();
const cardElement = elements.create('card');
cardElement.mount('#card-element');

document.getElementById('payment-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const { paymentMethod, error } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
    });
    
    if(error) {
        document.getElementById('card-errors').textContent = error.message;
    } else {
        // Enviar al backend
        document.getElementById('payment-form').submit();
    }
});
</script>

{% else %}
<div class="alert-error">
    <p>Debes iniciar sesión para proceder al pago.</p>
    <a href="{% url 'auth:login' %}?next={% url 'checkout' %}">Ir a login</a>
</div>
{% endif %}

</body>
</html>
```

---

## 📋 PASO 2: Vista para Crear PaymentIntent (Backend)

```python
# En apps/api/views.py (agregar):

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import stripe

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_pago_view(request):
    """
    POST /api/pago/crear_checkout/
    Crea PaymentIntent y orden desde carrito
    """
    try:
        usuario = request.user
        carrito = Carrito.objects.get(usuario=usuario)
        
        if carrito.items.count() == 0:
            return Response(
                {'error': 'Carrito vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener datos del formulario
        nombre = request.data.get('nombre')
        email = request.data.get('email')
        telefono = request.data.get('telefono')
        direccion = request.data.get('direccion')
        
        # Calcular total
        subtotal = float(carrito.total)
        shipping = 15.00
        tax = subtotal * 0.16
        total = subtotal + shipping + tax
        
        # Crear PaymentIntent en Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # Convertir a centavos
            currency='usd',
            metadata={
                'usuario_id': usuario.id,
                'usuario_email': email,
                'orden_numero': None  # Se actualizará después
            },
            customer_email=email,
        )
        
        # Crear pedido en BD
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=usuario,
                numero_pedido=f"ORD-{payment_intent.id[:12]}",
                estado='procesando',
                total=Decimal(str(total)),
                direccion_envio=direccion,
                telefono=telefono,
            )
            
            # Crear detalles del pedido desde carrito
            for item in carrito.items.all():
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    subtotal=item.subtotal,
                )
            
            # Crear registro de pago
            pago = Pago.objects.create(
                pedido=pedido,
                stripe_payment_intent_id=payment_intent.id,
                monto=Decimal(str(total)),
                estado='procesando',
            )
        
        # Actualizar metadata
        stripe.PaymentIntent.modify(
            payment_intent.id,
            metadata={'orden_numero': pedido.numero_pedido}
        )
        
        return Response({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'pedido_numero': pedido.numero_pedido,
            'total': float(total),
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
```

---

## 📋 PASO 3: Webhook de Confirmación (Stripe → Django)

```python
# En apps/api/views.py (agregar):

from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib

@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook_handler(request):
    """
    POST /api/pago/webhook/
    Procesa eventos de Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verificar firma de Stripe
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Procesar eventos
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Encontrar pago en BD
        try:
            pago = Pago.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            # Actualizar estado
            pago.estado = 'exitoso'
            pago.id_transaccion = payment_intent['id']
            pago.save()
            
            # Actualizar pedido
            pedido = pago.pedido
            pedido.estado = 'enviado'
            pedido.save()
            
            # TODO: Enviar email de confirmación
            # send_order_confirmation_email(pedido)
            
            # Limpiar carrito
            Carrito.objects.filter(usuario=pedido.usuario).update(
                actualizado_en=timezone.now()
            )
            ItemCarrito.objects.filter(
                carrito__usuario=pedido.usuario
            ).delete()
            
        except Pago.DoesNotExist:
            pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        try:
            pago = Pago.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            pago.estado = 'fallido'
            pago.razon_fallo = payment_intent.get('last_payment_error', {}).get('message')
            pago.save()
        except Pago.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'success'})
```

---

## 📋 PASO 4: Actualizar URLs

```python
# En apps/api/urls.py (agregar):

path('pago/crear_checkout/', crear_pago_view, name='crear_pago'),
path('pago/webhook/', stripe_webhook_handler, name='stripe_webhook'),
```

---

## 📝 PASO 5: Email de Confirmación (Bonus)

```python
# apps/api/emails.py (crear nuevo archivo):

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation(pedido):
    """Enviar email de confirmación de pedido"""
    
    context = {
        'pedido': pedido,
        'cliente': pedido.usuario.get_full_name(),
        'numero_seguimiento': pedido.numero_pedido,
    }
    
    html_message = render_to_string('emails/pedido_confirmado.html', context)
    
    send_mail(
        subject=f'Pedido Confirmado - {pedido.numero_pedido}',
        message='Tu pedido ha sido confirmado',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[pedido.usuario.email],
        html_message=html_message,
    )

# Usar en webhook:
send_order_confirmation(pago.pedido)
```

---

## 🎯 CHECKLIST IMPLEMENTACIÓN

- [ ] Crear `templates/checkout.html` con Stripe Elements
- [ ] Agregar `crear_pago_view` en views.py
- [ ] Agregar `stripe_webhook_handler` en views.py  
- [ ] Actualizar `apps/api/urls.py`
- [ ] Configura webhook en Stripe Dashboard:
  - [ ] Endpoint: `https://tu-dominio.com/api/pago/webhook/`
  - [ ] Eventos: `payment_intent.succeeded`, `payment_intent.payment_failed`
  - [ ] Obtener `signing_secret`
- [ ] Agregar botón "Proceder al Pago" en carrito.html
  - [ ] Redirige a `/checkout/`
- [ ] Crear template para página de confirmación

---

## 🧪 TESTING STRIPE

### 1. **En Modo Test**
```
Stripe Secret Key: sk_test_...
Stripe Public Key: pk_test_...
```

Tarjeta de prueba:
```
Número: 4242 4242 4242 4242
Exp: Cualquier fecha futura
CVC: Cualquier 3 dígitos
```

### 2. **Verificar Webhook Localmente**
```bash
# Instalar Stripe CLI
curl https://files.stripe.com/stripe-cli/install.sh | bash

# Escuchar eventos
stripe listen --forward-to localhost:8000/api/pago/webhook/

# En otra terminal: trigger evento
stripe trigger payment_intent.succeeded
```

### 3. **Verificar en Admin Django**
```
/admin/api/pago/
# Debe mostrar registros con estado 'exitoso'
```

---

## 📊 FLUJO COMPLETO FINAL

```
Cliente en Carrito
    ↓
Click "Proceder al Pago"
    ↓
Redirige a /checkout/
    ↓
Llenar formulario + Stripe Elements
    ↓
POST a /api/pago/crear_checkout/
    ↓
Crear PaymentIntent en Stripe
Crear Pedido en BD
Crear registro Pago
    ↓
Retorna client_secret
    ↓
Stripe procesa tarjeta en frontend
    ↓
✓ Exitoso → stripe.confirmCardPayment()
    ↓
Redirige a /pedido/{id}/
    ↓
Webhook /api/pago/webhook/
    ↓
Actualiza estado Pago + Pedido
Limpia carrito
Envía email confirmación
    ↓
✅ PEDIDO COMPLETADO
```

---

## 🚀 PRÓXIMAS OPTIMIZACIONES

- [ ] Confirmación por email elegante
- [ ] Página de tracking de pedido
- [ ] Historial de pedidos del usuario  
- [ ] Sistema de reembolsos
- [ ] Soporte para múltiples métodos pago (Apple Pay, Google Pay)
- [ ] Notificaciones SMS/WhatsApp

---

## 📞 RECURSOS STRIPE

- Dashboard: https://dashboard.stripe.com
- Documentación API: https://stripe.com/docs/api
- Testing: https://stripe.com/docs/testing
- Webhooks: https://stripe.com/docs/webhooks

---

**Status:** Ready to implement! 🚀
