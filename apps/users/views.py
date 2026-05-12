import random
import requests
from datetime import timedelta

from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

from apps.orders.models import Carrito
from .forms import RegistroForm
from .models import UserProfile, EmailOTP
from allauth.account.adapter import get_adapter
import logging

logger = logging.getLogger(__name__)


def _google_login_available(request):
    try:
        from allauth.socialaccount.models import SocialApp

        site = get_current_site(request)
        return SocialApp.objects.filter(provider='google', sites=site).exists()
    except Exception:
        return False


def _generate_otp_code(length=6):
    return ''.join(random.choices('0123456789', k=length))


def _authenticate_username_or_email(request, identifier, password):
    User = get_user_model()
    user = authenticate(request, username=identifier, password=password)
    if user is None and '@' in identifier:
        try:
            user_obj = User.objects.get(email__iexact=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
    return user


def _find_user_by_identifier(identifier):
    User = get_user_model()
    if '@' in identifier:
        return User.objects.filter(email__iexact=identifier).first()
    return User.objects.filter(username__iexact=identifier).first()


def _verify_recaptcha(request):
    """Valida el token de reCAPTCHA con Google."""
    recaptcha_response = request.POST.get('g-recaptcha-response')
    secret_key = getattr(settings, 'RECAPTCHA_PRIVATE_KEY', None)
    if not secret_key:
        return False, 'El sitio no está configurado para reCAPTCHA.'
    if not recaptcha_response:
        return False, 'Por favor completa el reCAPTCHA.'

    data = {'secret': secret_key, 'response': recaptcha_response}
    try:
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=10)
        r.raise_for_status()
        result = r.json()
        if not result.get('success'):
            return False, 'Verificación de CAPTCHA inválida. Inténtalo de nuevo.'
    except requests.exceptions.RequestException:
        return False, 'No se pudo conectar con el servicio reCAPTCHA.'

    return True, None


def _send_otp_email(user, code):
    subject = 'Aura Essence: Código temporal de acceso'
    message = (
        f'Tu código de verificación es: {code}\n\n'
        'El código expira en 3 minutos. No compartas este código con nadie.'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email], fail_silently=False)


def _create_pending_otp(request, user, next_url):
    EmailOTP.objects.filter(user=user, is_used=False, expires_at__gte=timezone.now()).update(is_used=True)
    code = _generate_otp_code()
    EmailOTP.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=3)
    )
    _send_otp_email(user, code)
    request.session['otp_user_id'] = user.id
    request.session['otp_next_url'] = next_url
    request.session.modified = True


def _clear_pending_otp(request):
    request.session.pop('otp_user_id', None)
    request.session.pop('otp_next_url', None)
    request.session.modified = True


def _email_verified(user):
    from allauth.account.models import EmailAddress
    return EmailAddress.objects.filter(user=user, email__iexact=user.email, verified=True).exists()


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
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Validación de reCAPTCHA
        success, error_msg = _verify_recaptcha(request)
        if not success:
            return render(request, 'auth/login.html', {
                'error': error_msg,
                'username': identifier,
                'google_login_available': _google_login_available(request),
                'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
            })
        
        if not identifier or not password:
            return render(request, 'auth/login.html', {
                'error': 'Usuario y contraseña son requeridos',
                'username': identifier,
                'google_login_available': _google_login_available(request),
                'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                'success': success_message,
            })

        # Usar el asistente para permitir login con nombre de usuario o email
        user = _authenticate_username_or_email(request, identifier, password)

        if user is not None:
            # Verificar si el email está verificado (excepto para staff/admin)
            if not user.is_staff and not user.is_superuser:
                if not _email_verified(user):
                    return render(request, 'auth/login.html', {
                        'error': 'Tu cuenta aún no ha sido verificada. Por favor, revisa tu correo electrónico.',
                        'username': identifier,
                        'google_login_available': _google_login_available(request),
                        'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                    })
            
            if not user.is_active:
                return render(request, 'auth/login.html', {
                    'error': 'Tu cuenta está pendiente de verificación. Revisa tu correo para activarla.',
                    'username': identifier,
                    'google_login_available': _google_login_available(request),
                    'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                })

            login(request, user)
            Carrito.objects.get_or_create(usuario=user)

            # Prioridad de redirección para administradores
            if user.is_superuser or user.is_staff:
                return redirect('/admin/')

            next_url = request.GET.get('next') or reverse('frontend:catalogo')
            return redirect(next_url)

        # Si el usuario existe pero aún no está activo/verificado, mostrar un mensaje claro
        candidate = _find_user_by_identifier(identifier)
        if candidate is not None:
            if not candidate.is_active:
                return render(request, 'auth/login.html', {
                    'error': 'Tu cuenta aún no ha sido activada. Revisa tu correo y usa el enlace de activación antes de iniciar sesión.',
                    'username': identifier,
                    'google_login_available': _google_login_available(request),
                    'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                    'success': success_message,
                })

            if not candidate.is_staff and not candidate.is_superuser and not _email_verified(candidate):
                return render(request, 'auth/login.html', {
                    'error': 'Tu correo todavía no está verificado. Revisa tu bandeja de entrada y confirma tu cuenta.',
                    'username': identifier,
                    'google_login_available': _google_login_available(request),
                    'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                    'success': success_message,
                })

        return render(request, 'auth/login.html', {
            'error': 'Usuario o contraseña incorrectos',
            'username': identifier,
            'google_login_available': _google_login_available(request),
            'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
            'success': success_message,
        })

    return render(request, 'auth/login.html', {
        'google_login_available': _google_login_available(request),
        'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
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


class ForcedPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'auth/password_change_form.html'
    success_url = reverse_lazy('auth:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        profile.must_change_password = False
        profile.save(update_fields=['must_change_password'])
        return response


class ForcedPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'auth/password_change_done.html'


def signup_view(request):
    """Vista de registro con validación de email y activación."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        recaptcha_success, recaptcha_error = _verify_recaptcha(request)
        
        if form.is_valid() and recaptcha_success:
            try:
                with transaction.atomic():
                    # Crear usuario inactivo
                    user = get_user_model().objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        is_active=False
                    )

                    # Enviar email de activación
                    _send_activation_email(request, user)

                messages.success(request, 'Cuenta creada exitosamente. Revisa tu correo para activar tu cuenta.')
                return redirect('auth:login')
            except Exception as e:
                logger.error(f"Error completo en el registro: {str(e)}")
                errores = {'general': f'No se pudo enviar el correo de activación: {str(e)}'}
                return render(request, 'auth/registro.html', {
                    'errores': errores,
                    'username': request.POST.get('username'),
                    'email': request.POST.get('email'),
                    'first_name': request.POST.get('first_name'),
                    'last_name': request.POST.get('last_name'),
                    'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
                })
        else:
            # Convertir errores del formulario al diccionario 'errores' que usa el HTML
            errores = {field: items[0] for field, items in form.errors.items()}
            if not recaptcha_success:
                errores['captcha'] = recaptcha_error
            return render(request, 'auth/registro.html', {
                'errores': errores,
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
            })
    else:
        form = RegistroForm()
    
    return render(request, 'auth/registro.html', {
        'form': form,
        'recaptcha_public_key': getattr(settings, 'RECAPTCHA_PUBLIC_KEY', ''),
    })


def activate_view(request, uidb64, token):
    """Vista de activación de cuenta."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Sincronizar con el sistema de Allauth para permitir el login posterior
        from allauth.account.models import EmailAddress
        email_obj, created = EmailAddress.objects.get_or_create(
            user=user, 
            email=user.email,
            defaults={'primary': True}
        )
        email_obj.verified = True
        email_obj.save()

        messages.success(request, 'Tu cuenta ha sido activada exitosamente. Ahora puedes iniciar sesión.')
        return redirect('auth:login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('auth:login')


def _send_activation_email(request, user):
    """Envía el email de activación."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('auth:activate', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Aura Essence: Activa tu cuenta'
    message = f"""
    ¡Hola {user.first_name}!

    Gracias por registrarte en Aura Essence. Para activar tu cuenta, haz clic en el siguiente enlace:

    {activation_link}

    Si no solicitaste esta cuenta, ignora este mensaje.

    Saludos,
    El equipo de Aura Essence
    """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    logger.info(f"Intentando conectar a SMTP: Host={settings.EMAIL_HOST}, Puerto={settings.EMAIL_PORT}, Usuario={settings.EMAIL_HOST_USER}, TLS={settings.EMAIL_USE_TLS}")
    try:
        send_mail(subject, message, from_email, [user.email], fail_silently=False)
    except Exception as e:
        logger.error(f"Excepción al enviar el email: {str(e)}")
        raise e
