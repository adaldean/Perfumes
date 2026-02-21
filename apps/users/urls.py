from django.urls import path, include
from . import views, admin_views
from . import api_views
# Como 'orders' maneja el carrito pero el namespace 'auth' se usaba para todo...
# Vamos a importar las views de orders AQUI para mantener rutas 'auth:carrito'
from apps.orders import views as order_views
from apps.orders import api_views as order_api_views

app_name = 'auth'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('gestion_clientes/', admin_views.gestion_usuarios_view, name='gestion_clientes'),
    path('api/registro/', api_views.RegistroView.as_view(), name='api_registro'),

    # Carrito (Mantenido en namespace 'auth' para compatibilidad)
    path('carrito/', order_views.carrito_view, name='carrito'),
    path('api/carrito/', order_api_views.carrito_api, name='carrito_api'),
    path('api/carrito/mercadopago/', order_api_views.CrearPagoView.as_view({'post': 'crear_preferencia_mp'}), name='pago_mp'),

    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
]
