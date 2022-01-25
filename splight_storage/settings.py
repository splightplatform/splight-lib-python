import os
import ast

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'storages',
    'splight_storage'
]

MEDIA_ROOT = "/data/media/"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "splight-api")


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
            "NAME": os.getenv("SQLITE_PATH", "/data/db.sqlite3"),
        }
    }

if ast.literal_eval(os.getenv("FAKE_STORAGE", "True")):
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
