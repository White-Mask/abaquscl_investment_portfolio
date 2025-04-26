# Investment Portfolio

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

Este proyecto es una aplicación Django diseñada para gestionar portafolios de inversión. Permite cargar datos desde archivos Excel, visualizar gráficos filtrados por portafolio y fechas, y gestionar transacciones de compra/venta.

## Índice

1. [Características Principales](#características-principales)
2. [Requisitos](#requisitos)
3. [Configuración del Proyecto](#configuración-del-proyecto)
4. [Ejecución del Proyecto](#ejecución-del-proyecto)
5. [Comandos Personalizados](#comandos-personalizados)
6. [Panel de Administración Gráfico](#panel-de-administración-gráfico)
---

## Características Principales

- **ETL (Extract, Transform, Load):** Procesa archivos Excel para cargar datos de portafolios, activos, precios y pesos.
- **Visualización de Gráficos:** Permite filtrar gráficos por portafolio y rango de fechas.
- **Transacciones:** Crea transacciones de compra/venta directamente desde la interfaz gráfica.
- **Panel de Administración:** Interfaz gráfica para subir archivos Excel y gestionar datos.


## Configuración del Proyecto

1. **Instalar Dependencias**

   Si no usas Docker, instala las dependencias manualmente:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar Variables de Entorno**

   Copia el archivo de ejemplo y configura las variables:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` con las credenciales necesarias:

   ```env
   DJANGO_SECRET_KEY='django-secret-key'
   DB_HOST=db
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASS=postgres
   DJANGO_SUPERUSER_PASSWORD=1234
   DJANGO_DEBUG=True
   DJANGO_DB_PORT=5432
   ```

## Ejecución del Proyecto

### Usando Docker Compose

1. Levanta los contenedores:

   ```bash
   docker-compose up --build
   ```

2. Accede al servidor Django en `http://localhost:8000`.

3. El superusuario se crea automáticamente:
   - **Usuario:** root
   - **Contraseña:** 1234

4. Consulta la documentación de los endpoints de la API en `http://localhost:8000/docs/`.


## Comandos Personalizados

### Procesar Archivo Excel

Procesa un archivo Excel desde la terminal:

```bash
python investment_portfolio/manage.py process_excel datos.xlsx 1 --initial-amount 1000000000
```

**Argumentos:**
- `datos.xlsx`: Ruta al archivo Excel.
- `1`: ID del usuario asociado.
- `--initial-amount`: Monto inicial del portafolio (opcional, predeterminado: 1,000,000,000).

## Panel de Administración Gráfico

### Subir Archivos Excel

1. Accede al panel en `http://localhost:8000/admin/cargar-excel/`.
2. Selecciona un usuario, carga un archivo Excel e ingresa el monto inicial.
3. Haz clic en "Subir y procesar".

### Visualizar Gráficos

1. Ve a `http://localhost:8000/admin/graficos-pre-evolucion/<id>/`.
2. Filtra por rango de fechas para ver los gráficos.

### Crear Transacciones

1. Accede a `http://localhost:8000/admin/graficos-trade/`.
2. Completa el formulario y guarda la transacción.
