"""
Vistas frontend para Autenticación y Carrito.
Maneja login, registro y lógica de carrito persistente.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
import logging

logger = logging.getLogger(__name__)

from .models import Carrito, ItemCarrito, Producto
from apps.catalog.models import Producto


# ============================================================
# VISTAS DE AUTENTICACIÓN FRONTEND
# ============================================================

@require_http_methods(["GET", "POST"])
def registro_view(request):
    """
    Vista para registro de nuevos usuarios.
    GET: Renderiza formulario de registro
    POST: Procesa registro
    """
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        # Validaciones
        errores = {}
        
        if not username or len(username) < 3:
            errores['username'] = 'El usuario debe tener mínimo 3 caracteres'
        
        if User.objects.filter(username=username).exists():
            errores['username'] = 'Este usuario ya existe'
        
        if not email or '@' not in email:
            errores['email'] = 'Email inválido'
        
        if User.objects.filter(email=email).exists():
            errores['email'] = 'Este email ya está registrado'
        
        if not password or len(password) < 6:
            errores['password'] = 'La contraseña debe tener mínimo 6 caracteres'
        
        if password != password2:
            errores['password2'] = 'Las contraseñas no coinciden'
        
        if errores:
            return render(request, 'auth/registro.html', {
                'errores': errores,
                'username': username,
                'email': email,
            })
        
        # Crear usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Crear carrito automáticamente
            Carrito.objects.get_or_create(usuario=user)
            
            # Migrar carrito de sesión si existe
            migrar_carrito_sesion(request, user)
            
            # Autenticar e iniciar sesión
            user = authenticate(request, username=username, password=password)
            login(request, user)
            
            # Redirigir a login con indicador query para mostrar alerta en frontend
            login_url = reverse('auth:login') + '?registered=1'
            return redirect(login_url)
            
        except Exception as e:
            return render(request, 'auth/registro.html', {
                'errores': {'general': f'Error al registrar: {str(e)}'},
                'username': username,
                'email': email,
            })
    
    return render(request, 'auth/registro.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista para iniciar sesión.
    GET: Renderiza formulario de login
    POST: Procesa login
    """
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            return render(request, 'auth/login.html', {
                'error': 'Usuario y contraseña son requeridos'
            })
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Crear carrito si no existe
            carrito, _ = Carrito.objects.get_or_create(usuario=user)
            
            # Migrar carrito de sesión
            migrar_carrito_sesion(request, user)
            
            # Redirigir al siguiente o al catálogo
            next_url = request.GET.get('next', 'frontend:catalogo')
            return redirect(next_url)
        else:
            return render(request, 'auth/login.html', {
                'error': 'Usuario o contraseña incorrectos',
                'username': username,
            })
    
    return render(request, 'auth/login.html')


@login_required(login_url='auth:login')
def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    return redirect('auth:login')


# ============================================================
# LÓGICA DE CARRITO (Sesión + Base de Datos)
# ============================================================

def obtener_carrito_sesion(request):
    """
    Obtiene el carrito guardado en sesión del navegador.
    Formato: {'producto_id': cantidad, ...}
    """
    return request.session.get('carrito', {})


def guardar_carrito_sesion(request, carrito_dict):
    """Guarda carrito en sesión."""
    request.session['carrito'] = carrito_dict
    request.session.modified = True


def migrar_carrito_sesion(request, user):
    """
    Migra productos del carrito de sesión al carrito persistente del usuario.
    Se ejecuta después de login/registro.
    """
    carrito_sesion = obtener_carrito_sesion(request)
    
    if not carrito_sesion:
        return  # No hay nada que migrar
    
    try:
        carrito_user = Carrito.objects.get(usuario=user)
        
        with transaction.atomic():
            for producto_id, cantidad in carrito_sesion.items():
                try:
                    producto = Producto.objects.get(id=int(producto_id))
                    item, created = ItemCarrito.objects.get_or_create(
                        carrito=carrito_user,
                        producto=producto,
                        defaults={'cantidad': 0}
                    )
                    # Sumar cantidades si el item ya existía
                    item.cantidad += int(cantidad)
                    item.save()
                except Producto.DoesNotExist:
                    continue
        
        # Limpiar sesión
        guardar_carrito_sesion(request, {})
        
    except Carrito.DoesNotExist:
        pass


# ============================================================
# VISTAS DE CARRITO (JSON API)
# ============================================================

@require_http_methods(["GET", "POST"])
def carrito_api(request):
    """
    API para gestionar carrito.
    GET: Obtiene carrito actual
    POST: Agrega producto al carrito
    """
    
    if request.method == "GET":
        return obtener_carrito(request)
    elif request.method == "POST":
        return agregar_carrito(request)


def obtener_carrito(request):
    """
    GET /api/carrito/
    Retorna el carrito actual (sesión o BD según si está autenticado).
    """
    if request.user.is_authenticated:
        # Carrito persistente
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            items = []
            for item in carrito.items.all():
                items.append({
                    'id': item.id,
                    'producto_id': item.producto.id,
                    'nombre': item.producto.nombre,
                    'precio': float(item.producto.precio),
                    'cantidad': item.cantidad,
                    'subtotal': float(item.subtotal),
                })
            
            return JsonResponse({
                'exito': True,
                'items': items,
                'total': float(carrito.total),
                'cantidad_items': carrito.cantidad_items,
            })
        except Carrito.DoesNotExist:
            return JsonResponse({'exito': False, 'error': 'Carrito no encontrado'})
    else:
        # Carrito de sesión
        carrito_sesion = obtener_carrito_sesion(request)
        items = []
        total = 0
        
        for producto_id, cantidad in carrito_sesion.items():
            try:
                producto = Producto.objects.get(id=int(producto_id))
                subtotal = float(producto.precio) * cantidad
                items.append({
                    'producto_id': producto.id,
                    'nombre': producto.nombre,
                    'precio': float(producto.precio),
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                })
                total += subtotal
            except Producto.DoesNotExist:
                continue
        
        return JsonResponse({
            'exito': True,
            'items': items,
            'total': total,
            'cantidad_items': len(items),  # Ojo: corregido para que el frontend lo use
        })


def agregar_carrito(request):
    """
    POST /api/carrito/
    Body: {'producto_id': int, 'cantidad': int}
    Agrega producto al carrito (sesión o BD).
    """
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
        
        if not producto_id or cantidad < 1:
            return JsonResponse({
                'exito': False,
                'error': 'Datos inválidos'
            }, status=400)
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        if request.user.is_authenticated:
            # Agregar a carrito persistente
            carrito = Carrito.objects.get(usuario=request.user)
            item, created = ItemCarrito.objects.get_or_create(
                carrito=carrito,
                producto=producto,
                defaults={'cantidad': 0}
            )
            item.cantidad += cantidad
            item.save()
        else:
            # Agregar a carrito de sesión
            carrito_sesion = obtener_carrito_sesion(request)
            carrito_sesion[str(producto_id)] = carrito_sesion.get(str(producto_id), 0) + cantidad
            request.session['carrito'] = carrito_sesion  # Guardar en sesión
            request.session.modified = True

        return JsonResponse({'exito': True, 'mensaje': 'Producto agregado'})
    except Exception as e:
        logger.error(f"Error agregando al carrito: {str(e)}")
        return JsonResponse({'exito': False, 'error': str(e)}, status=500)


@require_POST
def actualizar_carrito(request):
    """
    POST /api/carrito/actualizar/
    Body: {'producto_id': int, 'cantidad': int}
    Actualiza cantidad de un producto en el carrito.
    """
    try:
        data = json.loads(request.body)
        producto_id = int(data.get('producto_id'))
        cantidad = int(data.get('cantidad', 1))
        
        if cantidad <= 0:
            # Si cantidad es 0 o negativa, eliminar
            return eliminar_carrito(request)
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        if request.user.is_authenticated:
            # Actualizar en BD
            carrito = Carrito.objects.get(usuario=request.user)
            item = get_object_or_404(ItemCarrito, carrito=carrito, producto=producto)
            item.cantidad = cantidad
            item.save()
        else:
            # Actualizar en sesión
            carrito_sesion = obtener_carrito_sesion(request)
            if str(producto_id) in carrito_sesion:
                carrito_sesion[str(producto_id)] = cantidad
                guardar_carrito_sesion(request, carrito_sesion)
        
        return obtener_carrito(request)
    
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=400)


@require_POST
def eliminar_carrito(request):
    """
    POST /api/carrito/eliminar/
    Body: {'producto_id': int}
    Elimina un producto del carrito.
    """
    try:
        data = json.loads(request.body)
        producto_id = int(data.get('producto_id'))
        
        producto = get_object_or_404(Producto, id=producto_id)
        
        if request.user.is_authenticated:
            # Eliminar de BD
            carrito = Carrito.objects.get(usuario=request.user)
            ItemCarrito.objects.filter(carrito=carrito, producto=producto).delete()
        else:
            # Eliminar de sesión
            carrito_sesion = obtener_carrito_sesion(request)
            carrito_sesion.pop(str(producto_id), None)
            guardar_carrito_sesion(request, carrito_sesion)
        
        return obtener_carrito(request)
    
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=400)


# ============================================================
# VISTA DEL CARRITO (Frontend HTML)
# ============================================================

def carrito_view(request):
    """
    GET /carrito/
    Renderiza la página del carrito.
    """
    if request.user.is_authenticated:
        carrito = Carrito.objects.get(usuario=request.user)
        items = carrito.items.all()
        total = carrito.total
    else:
        carrito_sesion = obtener_carrito_sesion(request)
        items = []
        total = 0
        
        for producto_id, cantidad in carrito_sesion.items():
            try:
                producto = Producto.objects.get(id=int(producto_id))
                subtotal = producto.precio * cantidad
                items.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal,
                })
                total += subtotal
            except Producto.DoesNotExist:
                continue
    
    return render(request, 'carrito.html', {
        'items': items,
        'total': total,
        'es_autenticado': request.user.is_authenticated,
    })


# ============================================================
# VISTA DEL CHATBOT (Frontend HTML)
# ============================================================

def chatbot_view(request):
    """
    GET /chatbot/
    Renderiza la página del chatbot.
    """
    return render(request, 'chatbot.html')


# ============================================================
# FUNCIONES DE CHATBOT
# ============================================================

def detect_intent(message):
    """
    Detecta el intento del usuario.
    """
    keywords = {
        "catalogo": ["dama", "mujer", "niña", "hombre", "caballero", "niño", "joven", "fragancia", "loción", "aroma"],
        "promociones": ["oferta", "descuento", "rebaja", "promoción", "oportunidad", "barato", "económico"],
        "producto": ["dulce", "fresco", "intenso", "floral", "cítrico", "amaderado"],
        "compra": ["carrito", "disponibilidad", "forma de pago", "tipo de pago", "efectivo", "tarjeta", "costo", "precio"],
        "contacto": ["ayuda", "necesidad", "asistencia", "queja", "problema", "dificultad", "duda", "hablar", "contacto", "asesor"],
        "cierre": ["adiós", "gracias", "bye", "hasta luego", "no necesito nada"]
    }

    for intent, words in keywords.items():
        if any(word in message.lower() for word in words):
            return intent
    return "unknown"

def generate_response(intent, message, user):
    """
    Genera una respuesta basada en el intento.
    """
    if intent == "producto":
        # Filtrar productos según palabras clave
        aromas = ["dulce", "fresco", "intenso", "floral", "cítrico", "amaderado"]
        for aroma in aromas:
            if aroma in message.lower():
                productos = Producto.objects.filter(tipo_aroma__icontains=aroma)[:5]
                productos_data = [
                    {
                        "id": producto.id,
                        "nombre": producto.nombre,
                        "precio": f"{producto.precio:.2f}",
                        "imagen": producto.imagen.url if producto.imagen else ""
                    }
                    for producto in productos
                ]
                return {
                    "reply": f"Aquí tienes algunas opciones con aroma {aroma}:",
                    "productos": productos_data
                }
        return {"reply": "No encontré productos con esas características."}

    elif intent == "compra":
        return {"reply": "Aceptamos pagos en efectivo, tarjeta y transferencias. ¿Te gustaría más información?"}

    elif intent == "contacto":
        return {"reply": "Puedes contactarnos al correo soporte@auraessence.com o al teléfono 123-456-7890."}

    elif intent == "cierre":
        return {"reply": "Gracias por visitarnos. ¡Que tengas un excelente día!"}

    return {"reply": "Lo siento, no entendí tu mensaje. ¿Podrías reformularlo?"}

# Modificar chatbot_view para manejar productos dinámicos
@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            user = request.user if request.user.is_authenticated else None

            # Detect intent
            intent = detect_intent(message)

            # Generate response
            response = generate_response(intent, message, user)

            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"reply": "Hubo un error procesando tu mensaje. Por favor, intenta nuevamente."}, status=500)

    return JsonResponse({"reply": "Método no permitido."}, status=405)
