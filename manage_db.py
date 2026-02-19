#!/usr/bin/env python
"""
Pre-deployment database migration script
Ejecutar migraciones antes de que inicie gunicorn
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.management import call_command

try:
    print("→ Running migrations...")
    call_command('migrate', verbosity=1)
    print("✓ Migrations completed successfully")
except Exception as e:
    print(f"✗ Migration error: {e}")
    sys.exit(1)
