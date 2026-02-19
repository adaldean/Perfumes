from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import stripe
import json
import hmac
import hashlib

from .models import Producto, Pedido, DetallePedido, Pago
from .serializers import (
    ProductoSerializer, 
    RegistroSerializer, 
    UsuarioSerializer,
    PedidoSerializer,
    PagoSerializer,
    CrearPagoSerializer,
)
from .payments import StripePaymentManager
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# ============================================
# Vistas de Autenticación
# ============================================

class RegistroView(TokenObtainPairView):
    """
    Vista para registrar nuevos usuarios.
    POST /api/auth/registro/
    """
    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer
    
    def post(self, request, *args, **kwargs):
        """Registrar un nuevo usuario."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_201_CREATED)


# ============================================
# Vistas de Productos
# ============================================

class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Productos.
    Permite: GET (listar, obtener), POST/PUT/PATCH/DELETE (solo admin/staff)
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Permitir lectura sin autenticación, escritura solo autenticados."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


def catalogo(request):
    """Vista que renderiza el catálogo adaptado a la perfumería."""
    productos = Producto.objects.filter(activo=True).select_related('marca', 'categoria')[:48]

    # Intentar obtener categorías desde la tabla si existe
    categorias_qs = []
    try:
        from apps.api import models as api_models
        if hasattr(api_models, 'categorias'):
            categorias_qs = api_models.categorias.objects.all()
    except Exception:
        categorias_qs = []

    context = {
        'productos': productos,
        'categorias': categorias_qs,
    }
    return render(request, 'catalogo.html', context)


# ============================================
# Vistas de Pedidos
# ============================================

class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Pedidos.
    Los usuarios solo pueden ver sus propios pedidos.
    """
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Los usuarios solo ven sus propios pedidos."""
        return Pedido.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """Asociar el pedido al usuario actual."""
        serializer.save(usuario=self.request.user)


# ============================================
# Vistas de Pagos
# ============================================

class CrearPagoView(viewsets.ViewSet):
    """
    ViewSet para crear pagos con Stripe.
    POST /api/pago/crear/
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def crear(self, request):
        """
        Crear un PaymentIntent en Stripe.
        
        Body de la solicitud:
        {
            "pedido_id": 1,
            "email": "cliente@example.com",
            "nombre": "Juan Pérez"
        }
        """
        serializer = CrearPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            resultado = StripePaymentManager.crear_payment_intent(
                pedido_id=serializer.validated_data['pedido_id'],
                email=serializer.validated_data['email'],
                nombre=serializer.validated_data['nombre']
            )
            
            return Response(resultado, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error creando pago: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request):
        """Listar los pagos del usuario autenticado."""
        pagos = Pago.objects.filter(pedido__usuario=request.user)
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Webhook de Stripe para procesar eventos de pago.
    
    Este endpoint recibe notificaciones de Stripe cuando:
    - Un pago se completa exitosamente (payment_intent.succeeded)
    - Un pago falla (payment_intent.payment_failed)
    
    Actualiza automáticamente:
    - Estado del pago en la BD
    - Estado del pedido (si el pago es exitoso)
    
    URL: /api/pago/webhook/
    Eventos configurados en Stripe Dashboard:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    
    Para testing local:
    1. Instala Stripe CLI: https://stripe.com/docs/stripe-cli
    2. Ejecuta: stripe listen --forward-to localhost:8000/api/pago/webhook/
    3. Copia el signing secret a STRIPE_WEBHOOK_SECRET en .env
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Verificar la firma del webhook
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Payload inválido: {str(e)}")
        return JsonResponse({'error': 'Payload inválido'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Firma inválida: {str(e)}")
        return JsonResponse({'error': 'Firma inválida'}, status=400)
    
    # Procesar el evento
    if StripePaymentManager.procesar_webhook(event):
        logger.info(f"Webhook procesado exitosamente: {event['type']}")
    
    return JsonResponse({'success': True}, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def verificar_pago(request, payment_intent_id):
    """
    Verifica el estado actual de un PaymentIntent.
    
    URL: /api/pago/verificar/<payment_intent_id>/
    
    Retorna:
    {
        "status": "succeeded" | "processing" | "requires_payment_method",
        "monto": 99.99,
        "moneda": "USD",
        "estado_local": "exitoso" | "procesando" | "pendiente"
    }
    """
    try:
        resultado = StripePaymentManager.verificar_estado_pago(payment_intent_id)
        return JsonResponse(resultado, status=200)
    except Exception as e:
        logger.error(f"Error verificando pago: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
