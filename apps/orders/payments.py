"""
Módulo de Pagos con Stripe para Django.

Este módulo maneja la integración con Stripe para procesar pagos.
Incluye funciones para crear PaymentIntents y validar webhooks.

INSTRUCCIONES DE CONFIGURACIÓN INICIAL:
=====================================

1. Obtén tus claves de prueba en https://dashboard.stripe.com/test/keys
   - pk_test_XXXXXXXXX (Clave Pública de Prueba)
   - sk_test_XXXXXXXXX (Clave Secreta de Prueba)

2. Crea un archivo .env en la raíz del proyecto con:
   ```
   STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
   STRIPE_PUBLIC_KEY=pk_test_YOUR_PUBLIC_KEY_HERE
   STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_WEBHOOK_SECRET_HERE
   ```

3. Para obtener el webhook secret:
   - Ve a https://dashboard.stripe.com/test/webhooks
   - Crea un nuevo endpoint (Ctrl + Shift + P en VS Code: "Stripe")
   - URL del webhook: http://localhost:8000/api/pago/webhook/
   - Eventos a escuchar: payment_intent.succeeded, payment_intent.payment_failed
   - Copia el "Signing secret" (whsec_...) en el archivo .env

4. Para pruebas locales, usa:
   - Tarjetas de prueba: https://stripe.com/docs/testing
   - Número: 4242 4242 4242 4242
   - Fecha: cualquier fecha futura
   - CVC: cualquier 3 dígitos

5. Para testing con webhooks localmente:
   - Instala Stripe CLI: https://stripe.com/docs/stripe-cli
   - Ejecuta: stripe listen --forward-to localhost:8000/api/pago/webhook/
   - Copiar el signing secret a .env
"""

import stripe
from django.conf import settings
from django.utils import timezone
from .models import Pago, Pedido
import logging

# Configurar logging para pagos
logger = logging.getLogger(__name__)

# Configurar la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentManager:
    """Gestor de pagos con Stripe."""
    
    @staticmethod
    def crear_payment_intent(pedido_id, email, nombre):
        """
        Crea un PaymentIntent en Stripe para un pedido.
        
        Args:
            pedido_id (int): ID del pedido
            email (str): Email del cliente
            nombre (str): Nombre del cliente
            
        Returns:
            dict: Información del PaymentIntent con client_secret
            
        Raises:
            Exception: Si hay error al crear el PaymentIntent
        """
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Convertir el monto a centavos (Stripe usa centavos)
            monto_centavos = int(pedido.total * 100)
            
            # Crear PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='usd',
                metadata={
                    'pedido_id': str(pedido_id),
                    'numero_pedido': pedido.numero_pedido,
                    'usuario_id': str(pedido.usuario.id),
                },
                receipt_email=email,
                statement_descriptor=f"Pedido {pedido.numero_pedido}"
            )
            
            # Crear o actualizar registro de pago
            pago, _ = Pago.objects.update_or_create(
                pedido=pedido,
                defaults={
                    'stripe_payment_intent_id': payment_intent.id,
                    'monto': pedido.total,
                    'estado': 'procesando',
                }
            )
            
            logger.info(f"PaymentIntent creado: {payment_intent.id} para pedido {pedido_id}")
            
            return {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'monto': float(pedido.total),
                'numero_pedido': pedido.numero_pedido,
            }
            
        except Pedido.DoesNotExist:
            logger.error(f"Pedido no encontrado: {pedido_id}")
            raise Exception(f"Pedido con ID {pedido_id} no encontrado")
        except stripe.error.StripeError as e:
            logger.error(f"Error de Stripe: {str(e)}")
            raise Exception(f"Error al crear PaymentIntent: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            raise Exception(f"Error inesperado: {str(e)}")
    
    @staticmethod
    def procesar_webhook(event):
        """
        Procesa eventos de webhook de Stripe.
        
        Eventos soportados:
        - payment_intent.succeeded: Pago completado exitosamente
        - payment_intent.payment_failed: Pago fallido
        
        Args:
            event (dict): Evento de webhook de Stripe
            
        Returns:
            bool: True si se procesó correctamente
        """
        try:
            event_type = event['type']
            payment_intent = event['data']['object']
            
            # Obtener el ID del PaymentIntent
            pi_id = payment_intent['id']
            
            # Buscar el pago en la BD
            pago = Pago.objects.filter(stripe_payment_intent_id=pi_id).first()
            
            if not pago:
                logger.warning(f"Pago no encontrado para PaymentIntent: {pi_id}")
                return False
            
            # Procesar pago exitoso
            if event_type == 'payment_intent.succeeded':
                # Actualizar estado del pago
                pago.estado = 'exitoso'
                pago.id_transaccion = pi_id
                pago.metodo_pago = payment_intent.get('payment_method_details', {}).get('type', 'desconocido')
                pago.actualizado_en = timezone.now()
                pago.save()
                
                # Actualizar estado del pedido a "procesando"
                pedido = pago.pedido
                pedido.estado = 'procesando'
                pedido.actualizado_en = timezone.now()
                pedido.save()
                
                logger.info(f"Pago exitoso: {pi_id} - Pedido {pedido.numero_pedido}")
                return True
            
            # Procesar pago fallido
            elif event_type == 'payment_intent.payment_failed':
                razon = payment_intent.get('charges', {}).get('data', [{}])[0].get('failure_message', 'Razón desconocida')
                
                # Actualizar estado del pago
                pago.estado = 'fallido'
                pago.razon_fallo = razon
                pago.actualizado_en = timezone.now()
                pago.save()
                
                # Actualizar estado del pedido a "cancelado"
                pedido = pago.pedido
                pedido.estado = 'cancelado'
                pedido.actualizado_en = timezone.now()
                pedido.save()
                
                logger.warning(f"Pago fallido: {pi_id} - Razón: {razon}")
                return True
            
            else:
                logger.debug(f"Evento no procesado: {event_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            return False
    
    @staticmethod
    def verificar_estado_pago(payment_intent_id):
        """
        Verifica el estado actual de un PaymentIntent en Stripe.
        
        Args:
            payment_intent_id (str): ID del PaymentIntent
            
        Returns:
            dict: Estado del pago
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            pago = Pago.objects.filter(stripe_payment_intent_id=payment_intent_id).first()
            
            return {
                'status': payment_intent.status,
                'monto': payment_intent.amount / 100,  # Convertir de centavos
                'moneda': payment_intent.currency.upper(),
                'estado_local': pago.estado if pago else 'no_registrado',
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error verificando estado: {str(e)}")
            raise Exception(f"Error verificando estado: {str(e)}")
