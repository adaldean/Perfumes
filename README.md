# Proyecto Django Web

Un proyecto web completo desarrollado con **Django**, un framework web robusto y versátil de Python.

## Características

✅ Django 4.2.8 configurado  
✅ Django REST Framework para APIs  
✅ CORS configurado  
✅ Base de datos SQLite (configurable a PostgreSQL)  
✅ Sistema de administración Django  
✅ Estructura lista para escalar  

## Requisitos Previos

- Python 3.8+
- pip
- Virtual environment (ya configurado en `.venv/`)

## Instalación

1. **Activa el entorno virtual**
   ```bash
   source .venv/bin/activate  # En Linux/Mac
   # o
   .venv\Scripts\activate  # En Windows
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Realiza las migraciones**
   ```bash
   python manage.py migrate
   ```

4. **Crea un superusuario (administrador)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Inicia el servidor**
   ```bash
   python manage.py runserver
   ```

El servidor estará disponible en: http://127.0.0.1:8000

## Estructura del Proyecto

```
.
├── .github/
│   └── copilot-instructions.md
├── .venv/                      # Entorno virtual
├── myproject/                  # Configuración principal
│   ├── settings.py             # Configuraciones
│   ├── urls.py                 # Rutas principales
│   ├── wsgi.py                 # Configuración WSGI
│   └── __init__.py
├── apps/                       # Aplicaciones Django
├── templates/                  # Plantillas HTML
├── static/                     # Archivos estáticos (CSS, JS)
├── media/                      # Archivos multimedia
├── manage.py                   # Script de gestión
├── requirements.txt            # Dependencias
├── .env.example                # Variables de entorno (ejemplo)
└── README.md                   # Este archivo
```

## Crear una Nueva Aplicación

Para crear una nueva aplicación dentro del proyecto:

```bash
python manage.py startapp nombre_app
```

Luego, agrega la aplicación en `myproject/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'apps.nombre_app',
]
```

## Panel de Administración

Accede al panel de administración en: http://127.0.0.1:8000/admin/

Usa las credenciales del superusuario que creaste.

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `python manage.py runserver` | Inicia el servidor |
| `python manage.py migrate` | Aplica migraciones |
| `python manage.py makemigrations` | Crea migraciones |
| `python manage.py createsuperuser` | Crea un superusuario |
| `python manage.py startapp` | Crea una nueva aplicación |
| `python manage.py shell` | Inicia la consola interactiva |
| `python manage.py test` | Ejecuta las pruebas |

## Configuración de Base de Datos

### SQLite (Por defecto)
Sin configuración adicional, ya está lista.

### PostgreSQL
1. Instala el driver: `pip install psycopg2-binary`
2. Actualiza `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'myproject',
           'USER': 'postgres',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Django REST Framework

El proyecto incluye Django REST Framework para crear APIs REST.

Ejemplo de uso en una aplicación:

```python
from rest_framework import viewsets
from .models import Modelo
from .serializers import ModeloSerializer

class ModeloViewSet(viewsets.ModelViewSet):
    queryset = Modelo.objects.all()
    serializer_class = ModeloSerializer
```

## CORS

CORS está configurado para permitir solicitudes desde:
- `http://localhost:3000`
- `http://localhost:8000`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000`

Modifica `myproject/settings.py` para agregar más orígenes si es necesario.

## Variables de Entorno

Copia `.env.example` a `.env` y configura las variables según tu entorno:

```bash
cp .env.example .env
```

## Herramientas y Librerías Incluidas

- **Django 4.2.8**: Framework web
- **Django REST Framework**: Construcción de APIs
- **django-cors-headers**: Manejo de CORS
- **python-dotenv**: Gestión de variables de entorno
- **psycopg2-binary**: Driver para PostgreSQL

## Recursos Útiles

- [Documentación de Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)

## Licencia

Este proyecto está bajo la licencia MIT.

## Próximos Pasos

1. ✅ Entorno virtual configurado
2. ✅ Dependencias instaladas
3. ✅ Base de datos migrada
4. ✅ Superusuario creado
5. ✅ Servidor iniciado
6. 👉 **Crea tu primera aplicación**: `python manage.py startapp miapp`
7. 👉 **Define tus modelos** en `apps/miapp/models.py`
8. 👉 **Crea endpoints de API** con Django REST Framework
9. 👉 **Personaliza tu proyecto** según tus necesidades

---

**¡Listo para desarrollar! 🚀**
# Perfumes
