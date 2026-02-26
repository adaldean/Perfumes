from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .serializers import RegistroSerializer
from apps.orders.models import Carrito
from .models import UserProfile


def _google_login_available(request):
    """Indica si Google OAuth está configurado correctamente para el sitio actual."""
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.shortcuts import get_current_site

        site = get_current_site(request)
        return SocialApp.objects.filter(provider='google', sites=site).exists()
    except Exception:
        return False

def login_view(request):
    """
    Vista de Login.
    GET: Renderiza formulario
    POST: Procesa login
    """
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            return render(request, 'auth/login.html', {
                'error': 'Usuario y contraseña son requeridos',
                'google_login_available': _google_login_available(request),
            })
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Crear carrito si no existe
            Carrito.objects.get_or_create(usuario=user)
            
            # TODO: Migrar carrito de sesión (requiere lógica especial para importar desde orders)
            
            # Redirigir al admin si es superusuario o staff
            if user.is_superuser or user.is_staff:
                if not request.GET.get('next'):
                    return redirect('/admin/')
            
            # Redirigir al siguiente o al catálogo
            next_url = request.GET.get('next', 'frontend:catalogo')
            return redirect(next_url)
        else:
            return render(request, 'auth/login.html', {
                'error': 'Usuario o contraseña incorrectos',
                'username': username,
                'google_login_available': _google_login_available(request),
            })
    
    return render(request, 'auth/login.html', {
        'google_login_available': _google_login_available(request),
    })

@login_required(login_url='auth:login')
def logout_view(request):
    """Cerrar sesión."""
    logout(request)
    return redirect('auth:login')

@login_required(login_url='auth:login')
def perfil_view(request):
    """Vista del perfil de usuario."""
    return render(request, 'auth/perfil.html')

def registro_view(request):
    """Vista de registro (frontend)."""
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        errores = {}
        
        # Validaciones básicas
        if not username:
            errores['username'] = "El nombre de usuario es obligatorio."
        if not first_name:
            errores['first_name'] = "El nombre es obligatorio."
        if not last_name:
            errores['last_name'] = "El apellido es obligatorio."
        if not email:
            errores['email'] = "El correo electrónico es obligatorio."
        if not password:
            errores['password'] = "La contraseña es obligatoria."
        elif len(password) < 6:
            errores['password'] = "La contraseña debe tener al menos 6 caracteres."
        if password != password2:
            errores['password2'] = "Las contraseñas no coinciden."
            
        # Validar existencia de usuario
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            errores['username'] = "Este nombre de usuario ya está en uso."
        if User.objects.filter(email=email).exists():
            errores['email'] = "Este correo electrónico ya está registrado."
            
        if errores:
            return render(request, 'auth/registro.html', {
                'errores': errores,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })
            
        # Crear usuario
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Crear carrito
            Carrito.objects.get_or_create(usuario=user)
            
            # Iniciar sesión automáticamente
            login(request, user)
            
            return redirect('frontend:catalogo')

        except Exception as e:
            return render(request, 'auth/registro.html', {
                'errores': {'general': f'Error al crear la cuenta: {str(e)}'},
                'username': username,
                'email': email
            })

    return render(request, 'auth/registro.html')


class ForcedPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'auth/password_change_form.html'
    success_url = reverse_lazy('auth:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        profile.must_change_password = False
        profile.save(update_fields=['must_change_password'])
        return response


class ForcedPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'auth/password_change_done.html'
