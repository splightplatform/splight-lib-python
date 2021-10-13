import os
import django

if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'orm.settings'
    django.setup()