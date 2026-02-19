from django.urls import path
from .views import catalogo

app_name = 'frontend'

urlpatterns = [
    path('', catalogo, name='catalogo'),
]
