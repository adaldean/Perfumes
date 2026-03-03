from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def prevent_duplicate_model_registration(sender, **kwargs):
    # Evitar el registro duplicado del modelo Pago
    app_config = apps.get_app_config('orders')
    if 'pago' in app_config.models:
        print("Modelo 'Pago' ya registrado, evitando duplicados.")