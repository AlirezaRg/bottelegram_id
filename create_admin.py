import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get("DJANGO_ADMIN_USER", "admin")
password = os.environ.get("DJANGO_ADMIN_PASSWORD")
email = os.environ.get("DJANGO_ADMIN_EMAIL", "")

if not password:
    print("ERROR: set DJANGO_ADMIN_PASSWORD env var first")
    exit(1)

if User.objects.filter(username=username).exists():
    print(f"User {username} already exists - skipping")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created successfully")
