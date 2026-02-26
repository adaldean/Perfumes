import mercadopago
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class MercadoPagoManager:
    """Clase para gestionar pagos con Mercado Pago."""
    
    @staticmethod
    def crear_preferencia(items, usuario_email, back_urls):
        """
        Crea una preferencia de pago en Mercado Pago.
        
        Args:
            items: Lista de diccionarios con keys 'title', 'quantity', 'unit_price'
            usuario_email: Email del pagador
            back_urls: Diccionario con URLs de retorno
        """
        # Validar que la clave de Mercado Pago esté configurada
        if not getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', ''):
            raise ImproperlyConfigured(
                "MERCADOPAGO_ACCESS_TOKEN no configurado. Copia .env.example a .env o configura la variable de entorno en el servicio (Render)."
            )

        # SDK init
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        preference_data = {
            "items": items,
            "payer": {
                "email": usuario_email
            },
            "back_urls": back_urls,
            "auto_return": "approved",
        }
        
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        return preference
