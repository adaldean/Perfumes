from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from apps.orders.models import Carrito

from .models import UserProfile


def _google_login_available(request):
    """Indica si Google OAuth está configurado correctamente para el sitio actual."""
    try:
        from allauth.socialaccount.models import SocialApp

        site = get_current_site(request)
        return SocialApp.objects.filter(provider='google', sites=site).exists()
    except Exception:
        return False


def _build_activation_link(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return request.build_absolute_uri(
        reverse('auth:activar_cuenta', kwargs={'uidb64': uidb64, 'token': token})
    )


def _send_activation_email(request, user):
    current_site = get_current_site(request)
    activation_link = _build_activation_link(request, user)
    subject = 'Activa tu cuenta en Aura Essence'
    body = (
        f'Hola {user.username},\n\n'
        f'Gracias por registrarte en {current_site.domain}.\n'
        'Para activar tu cuenta, abre este enlace:\n\n'
        f'{activation_link}\n\n'
        'Si no creaste esta cuenta, puedes ignorar este correo.'
    )
    EmailMessage(subject, body, to=[user.email]).send(fail_silently=False)


def login_view(request):
    """
    Vista de Login.
    GET: Renderiza formulario
    POST: Procesa login
    """
    success_message = None
    if request.GET.get('verification_sent') == '1':
        success_message = 'Te enviamos un correo para activar tu cuenta.'
    elif request.GET.get('verified') == '1':
        success_message = 'Tu cuenta ya fue verificada. Ya puedes iniciar sesión.'

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'auth/login.html', {
                'error': 'Usuario y contraseña son requeridos',
                'username': username,
                'google_login_available': _google_login_available(request),
                'success': success_message,
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                return render(request, 'auth/login.html', {
                    'error': 'Tu cuenta está pendiente de verificación. Revisa tu correo para activarla.',
                    'username': username,
                    'google_login_available': _google_login_available(request),
                    'success': success_message,
                })

            login(request, user)
            Carrito.objects.get_or_create(usuario=user)

            if user.is_superuser or user.is_staff:
                if not request.GET.get('next'):
                    return redirect('/admin/')

            next_url = request.GET.get('next') or reverse('frontend:catalogo')
            return redirect(next_url)

        return render(request, 'auth/login.html', {
            'error': 'Usuario o contraseña incorrectos',
            'username': username,
            'google_login_available': _google_login_available(request),
            'success': success_message,
        })

    return render(request, 'auth/login.html', {
        'google_login_available': _google_login_available(request),
        'success': success_message,
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
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        errores = {}

        if not username:
            errores['username'] = 'El nombre de usuario es obligatorio.'
        if not first_name:
            errores['first_name'] = 'El nombre es obligatorio.'
        if not last_name:
            errores['last_name'] = 'El apellido es obligatorio.'
        if not email:
            errores['email'] = 'El correo electrónico es obligatorio.'
        if not password:
            errores['password'] = 'La contraseña es obligatoria.'
        elif len(password) < 6:
            errores['password'] = 'La contraseña debe tener al menos 6 caracteres.'
        if password != password2:
            errores['password2'] = 'Las contraseñas no coinciden.'

        if User.objects.filter(username=username).exists():
            errores['username'] = 'Este nombre de usuario ya está en uso.'
        if User.objects.filter(email=email).exists():
            errores['email'] = 'Este correo electrónico ya está registrado.'

        if errores:
            return render(request, 'auth/registro.html', {
                'errores': errores,
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()

            Carrito.objects.get_or_create(usuario=user)

            try:
                _send_activation_email(request, user)
            except Exception as email_error:
                user.delete()
                return render(request, 'auth/registro.html', {
                    'errores': {'general': f'No se pudo enviar el correo de verificación: {str(email_error)}'},
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                })

            return redirect(reverse('auth:login') + '?verification_sent=1')

        except Exception as e:
            return render(request, 'auth/registro.html', {
                'errores': {'general': f'Error al crear la cuenta: {str(e)}'},
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            })

    return render(request, 'auth/registro.html')


def activar_cuenta_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        return redirect(reverse('auth:login') + '?verified=1')

    return render(request, 'auth/login.html', {
        'error': 'El enlace de activación no es válido o ya expiró.',
        'google_login_available': _google_login_available(request),
    })


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
