from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.catalog.api_views import ProductoViewSet
from apps.orders.api_views import PedidoViewSet, CrearPagoView
from apps.users.api_views import RegistroView

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'pago', CrearPagoView, basename='pago')

app_name = 'api'

urlpatterns = [
    # Router
    path('', include(router.urls)),
    
    # Auth JWT
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/registro/', RegistroView.as_view(), name='registro'),
]
