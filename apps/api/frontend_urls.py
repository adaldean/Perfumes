from django.urls import path
from apps.catalog.views import catalogo, detalle_producto

app_name = 'frontend'

urlpatterns = [
    path('', catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', detalle_producto, name='detalle_producto'),
]


