import os

DATABASES = {
    "default": {
        "USER": os.getenv("MONGO_USER", "mongo"),
        "PASSWORD": os.getenv("MONGO_PASSWORD", "mongo"),
        "HOST": os.getenv("MONGO_HOST", "localhost"),
        "PORT": os.getenv("MONGO_PORT", ":27017"),
        "PROTOCOL": os.getenv("MONGO_PROTOCOL", "mongodb"),
    }
}

setup = DATABASES['default']
