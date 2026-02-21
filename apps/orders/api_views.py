from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json
import logging

from .models import Carrito, ItemCarrito, Pedido, DetallePedido, Pago
from .serializers import PedidoSerializer, CrearPagoSerializer
from apps.catalog.models import Producto
from .payments import StripePaymentManager
from .payments_mp import MercadoPagoManager # Importación agregada

logger = logging.getLogger(__name__)

# ============================================================
# LÓGICA DE CARRITO (Sesión + Base de Datos)
# ============================================================

def obtener_carrito_sesion(request):
    """
    Obtiene el carrito guardado en sesión del navegador.
    Formato: {'producto_id': cantidad, ...}
    """
    return request.session.get('carrito', {})

def carrito_api(request):
    """
    API para gestionar carrito.
    GET: Obtiene carrito actual
    POST: Agrega producto al carrito
    DELETE: Elimina producto del carrito
    """
    if request.method == "GET":
        return obtener_carrito(request)
    elif request.method == "POST":
        return agregar_carrito(request)
    elif request.method == "DELETE":
        return eliminar_de_carrito(request)

def obtener_carrito(request):
    """
    GET /api/carrito/
    Retorna el carrito actual (sesión o BD según si está autenticado).
    """
    if request.user.is_authenticated:
        try:
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            items = []
            for item in carrito.items.all():
                items.append({
                    'id': item.id,
                    'producto_id': item.producto.id,
                    'nombre': item.producto.nombre,
                    'precio': float(item.producto.precio),
                    'cantidad': item.cantidad,
                    'subtotal': float(item.subtotal),
                    'imagen': item.producto.imagen.url if item.producto.imagen else None
                })
            
            return JsonResponse({
                'exito': True,
                'items': items,
                'total': float(carrito.total),
                'cantidad_items': carrito.cantidad_items,
            })
        except Exception as e:
            return JsonResponse({'exito': False, 'error': str(e)})
    else:
        # Carrito de sesión
        carrito_sesion = obtener_carrito_sesion(request)
        items = []
        total = 0
        
        for producto_id, cantidad in carrito_sesion.items():
            try:
                producto = Producto.objects.get(id=int(producto_id))
                subtotal = float(producto.precio) * cantidad
                items.append({
                    'producto_id': producto.id,
                    'nombre': producto.nombre,
                    'precio': float(producto.precio),
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                    'imagen': producto.imagen.url if producto.imagen else None
                })
                total += subtotal
            except Producto.DoesNotExist:
                continue
        
        return JsonResponse({
            'exito': True,
            'items': items,
            'total': total,
            'cantidad_items': len(items),
        })

def agregar_carrito(request):
    """
    POST /api/carrito/
    Body: {'producto_id': int, 'cantidad': int}
    Agrega producto al carrito (sesión o BD).
    """
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
        
        # ... implementation ...
        producto = get_object_or_404(Producto, id=producto_id)
        
        if request.user.is_authenticated:
            # Agregar a carrito persistente
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            item, created = ItemCarrito.objects.get_or_create(
                carrito=carrito,
                producto=producto
            )
            
            # Si se acaba de crear, tiene cantidad=1 por default.
            # Lógica correcta: Si se creó, seteamos cantidad (normalmente 1).
            # Si ya existía, sumamos la cantidad.
            if created:
                item.cantidad = cantidad
            else:
                item.cantidad += cantidad
            item.save()
        else:
            # Agregar a carrito de sesión
            sid = str(producto_id)
            carrito_sesion = request.session.get('carrito', {})
            carrito_sesion[sid] = carrito_sesion.get(sid, 0) + cantidad
            request.session['carrito'] = carrito_sesion
            request.session.modified = True
            
        return JsonResponse({'exito': True, 'mensaje': 'Producto agregado'})
    except Exception as e:
        logger.error(f"Error agregando al carrito: {str(e)}")
        return JsonResponse({'exito': False, 'error': str(e)}, status=500)

def eliminar_de_carrito(request):
    """
    DELETE /api/carrito/
    Body: {'producto_id': int}
    Elimina producto del carrito completely.
    """
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')

        if not producto_id:
            return JsonResponse({'exito': False, 'error': 'ID de producto requerido'}, status=400)
            
        if request.user.is_authenticated:
            carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
            # Remove item for this product
            ItemCarrito.objects.filter(carrito=carrito, producto_id=producto_id).delete()
        else:
            sid = str(producto_id)
            carrito_sesion = request.session.get('carrito', {})
            if sid in carrito_sesion:
                del carrito_sesion[sid]
                request.session['carrito'] = carrito_sesion
                request.session.modified = True
        
        return JsonResponse({'exito': True, 'mensaje': 'Producto eliminado'})
    except Exception as e:
        return JsonResponse({'exito': False, 'error': str(e)}, status=500)


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

from .payments_mp import MercadoPagoManager

class CrearPagoView(viewsets.ViewSet):
    """
    ViewSet para crear pagos con Stripe y Mercado Pago.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def crear(self, request):
        """
        Crear Payment Intent (Stripe).
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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='mercadopago')
    def crear_preferencia_mp(self, request):
        """
        Crear preferencia de Mercado Pago.
        Body: { items: [{title, quantity, unit_price}], back_urls: {success, ...} }
        """
        try:
            # Obtener datos del carrito del usuario
            carrito = Carrito.objects.get(usuario=request.user)
            items = []
            for item in carrito.items.all():
                items.append({
                    "title": item.producto.nombre,
                    "quantity": item.cantidad,
                    "unit_price": float(item.producto.precio),
                    "currency_id": "MXN"
                })
            
            back_urls = {
                "success": request.build_absolute_uri('/perfil/#pedidos'),
                "failure": request.build_absolute_uri('/auth/carrito/'),
                "pending": request.build_absolute_uri('/auth/carrito/')
            }
            
            preference = MercadoPagoManager.crear_preferencia(
                items=items,
                usuario_email=request.user.email,
                back_urls=back_urls
            )
            
            return Response({'preference_id': preference['id'], 'init_point': preference['init_point']})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


