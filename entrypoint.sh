#!/bin/bash
set -e  # detener el script si ocurre un error

echo "🛠 Generando y aplicando migraciones…"
python investment_portfolio/manage.py makemigrations portfolios
python investment_portfolio/manage.py migrate

echo "Recolectando archivos estáticos..."
python investment_portfolio/manage.py collectstatic --no-input

# 4) Crear superusuario si no existe
echo "👤 Creando superusuario si no existe…"
python investment_portfolio/manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "root")
email    = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "1234")

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(username, email, password)
    print("✅ Superusuario creado:", username)
else:
    print("ℹ️  Ya existe un superusuario.")
EOF

# Inicia el servidor de desarrollo
echo "Iniciando servidor de desarrollo..."
exec python investment_portfolio/manage.py runserver 0.0.0.0:8000