import os
import sys
import ast

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'splight_database.django.djatabase'
]

TESTING = "test" in sys.argv
MEDIA_ROOT = "./media/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("SQLITE_PATH", "./db.sqlite3"),
    }
}
