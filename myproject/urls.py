"""
URL configuration for myproject project.
"""

import os

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from apps.core import views as core_views
from apps.api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # New Architecture URLs
    path('api/core/', include(('apps.core.api_urls', 'core-api'), namespace='core-api')),
    path('api/', include(('apps.api.urls', 'api'), namespace='api')),
    
    # Allauth URLs (Login con Google etc)
    path('accounts/', include('allauth.urls')),
    
    # Contacto
    path('contacto/', core_views.contacto_view, name='contacto'),

    # Legal
    path('legal/terminos/', core_views.terminos_view, name='terminos'),
    path('legal/privacidad/', core_views.privacidad_view, name='privacidad'),
    path('legal/devoluciones/', core_views.devoluciones_view, name='devoluciones'),
    path('legal/cookies/', core_views.cookies_view, name='cookies'),

    # Autenticación y carrito (Namespace 'auth')
    path('', include('apps.users.urls')),
    
    # Frontend: home -> index.html, catálogo en /catalogo/
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('catalogo/', include('apps.catalog.urls')),
]

# Servir media local también en producción cuando no hay S3 configurado.
if not os.getenv('AWS_STORAGE_BUCKET_NAME'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Archivos estáticos adicionales de desarrollo.
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
