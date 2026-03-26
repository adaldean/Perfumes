from django.urls import path
from . import views
from . import api_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'productos', api_views.ProductoViewSet)

app_name = 'frontend'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('api/best-sellers/', api_views.best_sellers, name='best_sellers'),
    path('api/genero/<str:genero>/', api_views.productos_por_genero, name='productos_por_genero'),
] + router.urls
