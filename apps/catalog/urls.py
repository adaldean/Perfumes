from django.urls import path
from . import views

app_name = 'frontend' # El nombre de la app se establece como 'frontend' para coincidir con el uso en base.html (ej. 'frontend:catalogo')

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('api/genero/<str:genero_param>/', views.api_productos_por_genero, name='api_productos_por_genero'),
    path('api/categoria/<str:categoria_param>/', views.api_productos_por_categoria, name='api_productos_por_categoria'),
    path('api/best-sellers/', views.api_best_sellers, name='api_best_sellers'),
]