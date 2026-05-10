#!/usr/bin/env python
"""
Script para crear usuarios iniciales en producción.
Se ejecuta durante el despliegue en Render.
"""

import os
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

def create_initial_users():
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
        print(f"Superusuario '{admin_username}' creado.")

        # Marcar email como verificado
        EmailAddress.objects.get_or_create(
            user=user,
            email=admin_email,
            defaults={
                'primary': True,
                'verified': True
            }
        )
        print(f"Email '{admin_email}' marcado como verificado.")
    else:
        print(f"Superusuario '{admin_username}' ya existe.")

if __name__ == '__main__':
    create_initial_users()