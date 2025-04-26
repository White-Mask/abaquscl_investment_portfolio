# investment_portfolio/config/settings/dev.py
from ..base import *

# Durante desarrollo:
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Base de datos dev (si quieres valores por defecto distintos)
DATABASES["default"].update({
    "NAME":     os.getenv("DJANGO_DB_NAME", "dev_db"),
    "USER":     os.getenv("DJANGO_DB_USER", "dev_user"),
    "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "dev_password"),
    "HOST":     os.getenv("DJANGO_DB_HOST", "localhost"),
    "PORT":     os.getenv("DJANGO_DB_PORT", "5432"),
})
