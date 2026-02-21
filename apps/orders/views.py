from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Carrito, ItemCarrito
from apps.catalog.models import Producto

def carrito_view(request):
    """Vista HTML del carrito de compras."""
    return render(request, 'carrito.html', {
        'MERCADOPAGO_PUBLIC_KEY': getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', 'TEST-3af62602-4fc4-4780-9989-13e87850a12e')
    })

