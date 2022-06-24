import os
import django
import shutil
from pathlib import Path
from .settings import DATABASE_HOME
DEFAULT_DATABASE = os.path.join(Path(__file__).resolve().parent, 'db.sqlite3')

if not os.path.exists(os.path.join(DATABASE_HOME, "db.sqlite3")):
    shutil.copy(DEFAULT_DATABASE, os.path.join(DATABASE_HOME, "db.sqlite3"))


from django.apps import apps
from django.conf import settings
if not apps.ready and not settings.configured:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'splight_database.django.settings'
    django.setup()