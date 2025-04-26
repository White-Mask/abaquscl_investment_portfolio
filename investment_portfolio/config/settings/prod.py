from ..base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Database configuration for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "prod_db"),
        "USER": os.getenv("DJANGO_DB_USER", "prod_user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "prod_password"),
        "HOST": os.getenv("DJANGO_DB_HOST", "prod-db-host"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}

# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files served by a web server (e.g., Nginx)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")