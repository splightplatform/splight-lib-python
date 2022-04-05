import os
import sys
import ast
from splight_lib.settings import SPLIGHT_HOME

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'splight_database.django.djatabase'
]

DATABASE_HOME = os.path.join(SPLIGHT_HOME, "database")

TESTING = "test" in sys.argv or "pytest" in sys.argv

MEDIA_ROOT = os.path.join(DATABASE_HOME, "media")
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME", "postgres"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

if TESTING or os.getenv("DATABASE_TYPE", "SQLITE") == "SQLITE":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(DATABASE_HOME, "db.sqlite3"),
        }
    }