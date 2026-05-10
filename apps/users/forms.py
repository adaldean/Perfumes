from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from apps.core.services import validate_email


class CustomSignupForm(SignupForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def save(self, request):
        user = super().save(request)
        return user

class RegistroForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(min_length=3, max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput, min_length=6)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        # Validación básica de formato
        if not email or '@' not in email:
            raise forms.ValidationError('Formato de correo inválido.')
        
        # Validación con Hunter.io
        validation_result = validate_email(email)
        if validation_result['status'] == 'error':
            # Si hay error en la API, permitir continuar pero loggear
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error validando email {email}: {validation_result.get('message', 'Unknown error')}")
        elif validation_result['status'] == 'invalid':
            raise forms.ValidationError('Este correo electrónico es inválido o desechable. Por favor, utiliza un correo válido.')
        elif validation_result['status'] == 'risky':
            raise forms.ValidationError('Este correo electrónico es considerado riesgoso. Por favor, utiliza un correo diferente.')
        # Solo permitir si es 'valid'
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
