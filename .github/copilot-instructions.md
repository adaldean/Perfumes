# Instrucciones del Proyecto Django

Este es un proyecto web desarrollado con Django, un framework web de Python.

## Estructura del Proyecto

- `myproject/` - Carpeta principal del proyecto Django
  - `settings.py` - Configuraciones del proyecto
  - `urls.py` - URLs principales
  - `wsgi.py` - Configuración WSGI
- `apps/` - Aplicaciones Django
- `manage.py` - Script de gestión de Django
- `requirements.txt` - Dependencias del proyecto

## Primeros Pasos

1. El entorno virtual está configurado en `.venv/`
2. Instala las dependencias con: `pip install -r requirements.txt`
3. Realiza migraciones: `python manage.py migrate`
4. Crea un superusuario: `python manage.py createsuperuser`
5. Inicia el servidor: `python manage.py runserver`

## Base de Datos

Por defecto usa SQLite. Para cambiar a PostgreSQL, actualiza `settings.py`.

## Adiciones Realizado

- Django 4.2.8 instalado
- Django REST Framework incluido
- CORS headers configurado
- Estructura de proyecto lista
