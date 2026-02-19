"""
URL configuration for myproject project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('apps.api.urls')),
    
    # Autenticación y carrito
    path('', include('apps.api.auth_urls')),
    
    # Frontend: home -> index.html, catálogo en /catalogo/
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('catalogo/', include('apps.api.frontend_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
