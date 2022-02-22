import os
import django

if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splight_database.django.settings')
    django.setup()
