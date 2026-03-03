from django.contrib.auth import get_user_model
import os

def create_admin_user():
    User = get_user_model()
    username = os.getenv('ADMIN_USERNAME', 'adal')
    email = os.getenv('ADMIN_EMAIL', 'adal.domingo13@outlook.com')
    password = os.getenv('ADMIN_PASSWORD', '123456')

    if not User.objects.filter(username=username).exists():
        print(f"Creating admin user: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print(f"Admin user {username} already exists.")

if __name__ == '__main__':
    create_admin_user()