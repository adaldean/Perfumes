"""
URL configuration for myproject project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    
    # New Architecture URLs
    path('api/', include('apps.core.api_urls')),
    
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
