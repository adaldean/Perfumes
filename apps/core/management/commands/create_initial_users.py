from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
import os

class Command(BaseCommand):
    help = 'Crear usuarios iniciales'

    def handle(self, *args, **options):
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'securepassword')

        # Crear superusuario si no existe
        if not User.objects.filter(username=admin_username).exists():
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{admin_username}' creado."))

            # Marcar email como verificado
            EmailAddress.objects.get_or_create(
                user=user,
                email=admin_email,
                defaults={
                    'primary': True,
                    'verified': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Email '{admin_email}' marcado como verificado."))
        else:
            self.stdout.write(self.style.WARNING(f"Superusuario '{admin_username}' ya existe."))