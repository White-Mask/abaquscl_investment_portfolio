from ..base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Database configuration for staging
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "staging_db"),
        "USER": os.getenv("DJANGO_DB_USER", "staging_user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "staging_password"),
        "HOST": os.getenv("DJANGO_DB_HOST", "staging-db-host"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}