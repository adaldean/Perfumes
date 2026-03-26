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

## Configuración de la Base de Datos (PostgreSQL)

### Requisitos Previos
- Asegúrate de tener PostgreSQL instalado en tu sistema. En Linux Mint, puedes instalarlo con:
  ```bash
  sudo apt update
  sudo apt install postgresql postgresql-contrib
  ```

### Crear la Base de Datos y el Usuario
1. Accede a PostgreSQL:
   ```bash
   sudo -u postgres psql
   ```

2. Crea la base de datos:
   ```sql
   CREATE DATABASE perfumeria;
   ```

3. Crea el usuario con su contraseña:
   ```sql
   CREATE USER administrador1 WITH PASSWORD 'tu_contraseña_segura';
   ```

4. Otorga permisos al usuario sobre la base de datos:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE perfumeria TO administrador1;
   ```

5. Sal de PostgreSQL:
   ```sql
   \q
   ```

### Configurar el Acceso Local
1. Edita el archivo `pg_hba.conf` para permitir conexiones locales con contraseña:
   ```bash
   sudo nano /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf
   ```

2. Asegúrate de que las siguientes líneas estén configuradas como `md5`:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            md5
   # IPv6 local connections:
   host    all             all             ::1/128                 md5
   ```

3. Reinicia PostgreSQL para aplicar los cambios:
   ```bash
   sudo systemctl restart postgresql
   ```

### Configurar el Proyecto Django
1. Asegúrate de que el archivo `.env` esté configurado correctamente:
   ```env
   POSTGRES_DB=perfumeria
   POSTGRES_USER=administrador1
   POSTGRES_PASSWORD=tu_contraseña_segura
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

2. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```

3. Carga los datos iniciales (opcional):
   ```bash
   python manage.py shell < scripts/create_sample_data.py
   python manage.py shell < scripts/seed_more_products.py
   ```

### Verificar la Configuración
- Inicia el servidor de desarrollo:
  ```bash
  python manage.py runserver
  ```
- Accede a la aplicación y verifica que los datos estén cargados correctamente.

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