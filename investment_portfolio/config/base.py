# investment_portfolio/config/base.py

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# 1) Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2) Carga variables de entorno de .env (debe existir en BASE_DIR)
load_dotenv(BASE_DIR / ".env")

# 3) Seguridad
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Falta DJANGO_SECRET_KEY en el .env")

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

# 4) Hosts permitidos (lista separada por comas)
_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _hosts.split(",") if h.strip()]

# 5) Aplicaciones instaladas
INSTALLED_APPS = [
    "apps.admin_custom",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.portfolios",
    "rest_framework",
    "drf_spectacular",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Investment Portfolio API",
    "DESCRIPTION": "API para visualizar y rebalancear portafolios de inversión.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# 6) Middleware (añadimos WhiteNoise para servir estáticos)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",        # <–– sirve estáticos en prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 7) Base de datos por defecto (puedes usar DATABASE_URL o las variables individuales)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":     os.getenv("DJANGO_DB_NAME", "db"),
        "USER":     os.getenv("DJANGO_DB_USER", "user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "password"),
        "HOST":     os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT":     os.getenv("DJANGO_DB_PORT", "5432"),
    }
}

# 8) Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 9) Internacionalización
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# 10) Archivos estáticos
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Con WhiteNoise optimizas entrega de estáticos en producción:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 11) Campo por defecto en modelos
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
