# Aura Essence

E-commerce de perfumería desarrollado con Django + Django REST Framework.

## Stack actual
- Python 3.11+
- Django 6
- Django REST Framework + JWT
- Allauth (Google)
- WhiteNoise (estáticos en producción)
- Render (web service + PostgreSQL vía `render.yaml`)

## Estructura del proyecto
- `myproject/`: configuración global (`settings.py`, `urls.py`, `wsgi.py`)
- `apps/catalog/`: catálogo, productos, vistas frontend y API
- `apps/orders/`: carrito, pedidos, pago
- `apps/users/`: autenticación, perfil y endpoints de usuario
- `apps/core/`: rutas API principales y vistas de páginas estáticas
- `templates/`: HTML del frontend y admin custom
- `static/`, `media/`: recursos estáticos y subidas
- `scripts/template_guard.py`: detector/corrector de expresiones Django multilinea

## Configuración local (desarrollo)

### 1) Crear entorno e instalar dependencias
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Variables de entorno
Copiar `.env.example` a `.env` y ajustar valores.

Variables clave:
- `DEBUG=True`
- `SECRET_KEY=...`
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `CSRF_TRUSTED_ORIGINS=http://localhost:8000`
- `DATABASE_URL=` (vacío para SQLite local, o URL Postgres)

### 3) Migraciones y usuario admin
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4) Ejecutar servidor
```bash
python manage.py runserver
```

## Flujo de precios y descuentos (admin)
- `precio`: precio normal del producto.
- `precio_oferta` (opcional): si existe, se muestra como precio actual y `precio` aparece tachado.
- Validación implementada: `precio_oferta` debe ser menor que `precio`.
- El badge **Oferta** se muestra en catálogo cuando el producto tiene `precio_oferta`.

## Endpoints principales

### Frontend
- `/` inicio
- `/catalogo/` listado
- `/catalogo/producto/<id>/` detalle de producto
- `/carrito/`
- `/perfil/`

### API
Base: `/api/`
- `GET /api/productos/`
- `GET/POST /api/pedidos/`
- `POST /api/pago/...` (acciones del `ViewSet`)
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/registro/`

### Auth clásica
- `/login/`
- `/logout/`
- `/registro/`
- `/accounts/` (allauth)

## Protección contra autoformateo de plantillas

Se añadió una protección para evitar que aparezcan tokens literales como `{{ cat.nombre }}` en frontend:

1. Configuración VS Code en `.vscode/settings.json` para `django-html`.
2. Script `scripts/template_guard.py`.

### Uso del guard
```bash
# Solo revisar
python scripts/template_guard.py

# Revisar y corregir automáticamente
python scripts/template_guard.py --fix
```

El script recorre `templates/**/*.html` y colapsa expresiones `{{ ... }}` que hayan quedado partidas en varias líneas.

## Despliegue en Render (paso a paso)

Este repo ya incluye `render.yaml` (Blueprint). Recomendado usar esa vía.

### Opción A: Blueprint (recomendada)
1. En Render: **New** → **Blueprint**.
2. Conectar este repositorio.
3. Render leerá `render.yaml` y creará:
   - Web service `aura-essence-api`
   - PostgreSQL `aura-essence-db`
4. Esperar build/deploy y abrir la URL `.onrender.com`.

### Opción B: Manual (si no usas Blueprint)
Crear un **Web Service** con:
- Runtime: Python
- Build Command:
  - `pip install -r requirements.txt && python manage.py collectstatic --no-input`
- Start Command:
  - `python manage.py migrate --noinput && gunicorn myproject.wsgi:application`

Agregar variables mínimas:
- `SECRET_KEY` (segura)
- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`
- `DATABASE_URL=<connection string de Render Postgres>`
- `PYTHON_VERSION=3.11.8`

## Checklist post-despliegue
- `/admin/` abre correctamente
- `/catalogo/` renderiza sin tokens `{{...}}` literales
- Estáticos cargan (CSS/JS)
- Login y carrito funcionan
- Si usas pagos, validar credenciales en variables de entorno

## Comandos útiles
```bash
# Comprobación general Django
python manage.py check

# Ejecutar migraciones
python manage.py migrate

# Recolectar estáticos (producción)
python manage.py collectstatic --no-input
```