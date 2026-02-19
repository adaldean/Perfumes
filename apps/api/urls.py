from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    ProductoViewSet,
    PedidoViewSet,
    CrearPagoView,
    RegistroView,
    stripe_webhook,
    verificar_pago,
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'pago', CrearPagoView, basename='pago')

app_name = 'api'

urlpatterns = [
    # Rutas del router (productos, pedidos, pago)
    path('', include(router.urls)),
    
    # ==========================================
    # Autenticación con JWT
    # ==========================================
    # POST /api/auth/login/
    # Body: {"username": "...", "password": "..."}
    # Retorna: {"access": "...", "refresh": "..."}
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST /api/auth/refresh/
    # Body: {"refresh": "..."}
    # Retorna: {"access": "..."}
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # POST /api/auth/registro/
    # Body: {"username": "...", "email": "...", "password": "...", "password2": "..."}
    # Retorna: {"message": "...", "user_id": "...", ...}
    path('auth/registro/', RegistroView.as_view(), name='registro'),
    
    # ==========================================
    # Pagos y Webhooks (Stripe)
    # ==========================================
    # POST /api/pago/crear/
    # Body: {"pedido_id": 1, "email": "...", "nombre": "..."}
    # Retorna: {"client_secret": "...", "payment_intent_id": "...", ...}
    # (Ya incluido en router)
    
    # GET /api/pago/verificar/<payment_intent_id>/
    path('pago/verificar/<str:payment_intent_id>/', verificar_pago, name='verificar_pago'),
    
    # POST /api/pago/webhook/
    # Endpoint para webhooks de Stripe (configurar en Stripe Dashboard)
    path('pago/webhook/', stripe_webhook, name='stripe_webhook'),
]
