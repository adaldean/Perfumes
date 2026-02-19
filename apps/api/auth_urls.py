from django.urls import path
from .auth_views import (
    login_view,
    logout_view,
    registro_view,
    carrito_api,
    actualizar_carrito,
    eliminar_carrito,
    carrito_view,
)

app_name = 'auth'

urlpatterns = [
    # Autenticación
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),
    
    # Carrito
    path('carrito/', carrito_view, name='carrito'),
    path('api/carrito/', carrito_api, name='carrito_api'),
    path('api/carrito/actualizar/', actualizar_carrito, name='actualizar_carrito'),
    path('api/carrito/eliminar/', eliminar_carrito, name='eliminar_carrito'),
]
