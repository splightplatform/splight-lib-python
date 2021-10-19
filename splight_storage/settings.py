from pathlib import Path
import os

db_location = "db.sqlite3" if os.name == "nt" else "/tmp/db.sqlite3"

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = 'django-insecure-18t7f*be*9+x1tgshn66b)f#ryv0_m7m9gf65x@$yrz5x%t4xl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'splight_storage'
]

# TODO set this from parameters
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": db_location
    }
}

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

API_URL = 'http://localhost:8005'
