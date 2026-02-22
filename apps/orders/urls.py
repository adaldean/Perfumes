from django.urls import path
from . import views
from . import api_views

# Mantener compatibilidad con namespace 'auth' para carrito de momento, 
# o cambiar templates. El usuario pidio no romper nada.
# Los templates usan 'auth:carrito'. Asi que definiremos app_name='orders'
# y añadiremos estas urls a las de users bajo namespace 'auth' o 
# actualizaremos los templates.
# Mejor: Definir namespace 'orders' y actualizar templates DE UNA VEZ, es mas limpio.
# PERO "sin romper codigo" suele significar "sin cambiar llamadas".
# Si cambio namespace, tengo que editar templates.
# Voy a intentar mantener namespace 'auth' en users e incluir orders alli.

app_name = 'orders'

urlpatterns = [
    path('carrito/', views.carrito_view, name='carrito'),
    path('api/carrito/', api_views.carrito_api, name='carrito_api'),
    path('api/carrito/actualizar/', api_views.carrito_api, name='actualizar_carrito'), # TODO: implementar actualizar
]
