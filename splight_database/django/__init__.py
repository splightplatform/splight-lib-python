import os
import django
from django.apps import apps
from django.conf import settings

if not apps.ready and not settings.configured:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'splight_database.django.settings'
    django.setup()