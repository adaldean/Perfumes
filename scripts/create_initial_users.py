#!/usr/bin/env python3
import os
import secrets
import sys
from pathlib import Path

# Ensure project root is on sys.path so `myproject` is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
User = get_user_model()

def ensure_user(username, email, is_super=False):
    u = User.objects.filter(username=username).first()
    if u:
        changed = False
        if u.email != email:
            u.email = email
            changed = True
        if u.is_staff != is_super:
            u.is_staff = is_super
            changed = True
        if u.is_superuser != is_super:
            u.is_superuser = is_super
            changed = True
        if changed:
            u.save()
        created = False
        pwd = None
        profile, _ = UserProfile.objects.get_or_create(user=u)
    else:
        pwd = secrets.token_urlsafe(12)
        try:
            if is_super and hasattr(User.objects, 'create_superuser'):
                u = User.objects.create_superuser(username=username, email=email, password=pwd)
                created = True
            else:
                u = User.objects.create_user(username=username, email=email, password=pwd)
                u.is_staff = is_super
                u.is_superuser = is_super
                u.save()
                created = True
        except TypeError:
            # fallback if create_superuser signature differs
            u = User.objects.create_user(username=username, email=email, password=pwd)
            u.is_staff = is_super
            u.is_superuser = is_super
            u.save()
            created = True

        profile, _ = UserProfile.objects.get_or_create(user=u)
        profile.must_change_password = True
        profile.save(update_fields=['must_change_password'])

    return pwd, created

def main():
    pairs = [
        ("Adal", "adal@gmail.com", "123456aa", True),
        ("Joss", "jossA@example.com", "OtraSegura123", True),
    ]

    results = []
    for username, email, is_super in pairs:
        try:
            pwd, created = ensure_user(username, email, is_super)
        except Exception as e:
            print(f"ERROR processing {username}: {e}", file=sys.stderr)
            pwd = None
            created = False
        results.append((username, email, is_super, pwd, created))

    for username, email, is_super, pwd, created in results:
        role = 'superuser' if is_super else 'user'
        status = 'created' if created else 'updated'
        if pwd:
            print(f"{username} ({email}) [{role}] {status}: password={pwd}")
        else:
            print(f"{username} ({email}) [{role}] {status}: password=UNCHANGED")

if __name__ == '__main__':
    main()
