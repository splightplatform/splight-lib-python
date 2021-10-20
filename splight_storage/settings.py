import os

db_location = "db.sqlite3" if os.name == "nt" else "/tmp/db.sqlite3"

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'splight_storage'
]

# TODO set this from parameters
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": db_location
    }
}
