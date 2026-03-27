from django.urls import path
from . import views
from . import api_views

app_name = 'orders'

urlpatterns = [
    path('carrito/', views.carrito_view, name='carrito'),
    path('api/carrito/', api_views.carrito_api, name='carrito_api'),
    path('api/carrito/actualizar/', api_views.carrito_api, name='actualizar_carrito'),
]
