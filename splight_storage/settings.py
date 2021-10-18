from pathlib import Path
import os

db_location = "db.sqlite3" if os.name == "nt" else "/tmp/db.sqlite3"

DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent


INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'splight_storage'
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": db_location
    }
}
