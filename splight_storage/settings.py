import os
import ast


db_location = "db.sqlite3" if os.name == "nt" else "/tmp/db.sqlite3"

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'splight_storage'
]


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

if ast.literal_eval(os.getenv("FAKE_DATABASE", "True")):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("POSTGRES_PORT", "/data/db.sqlite3"),
        }
    }
