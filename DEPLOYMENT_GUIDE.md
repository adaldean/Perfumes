# 🚀 GUÍA DE DEPLOYMENT - AURA ESSENCE

## 📋 ÍNDICE
1. [Preparación Local](#preparación-local)
2. [Opción A: Render (Recomendado)](#opción-a-render-recomendado)
3. [Opción B: PythonAnywhere](#opción-b-pythonanywhere)
4. [Post-Deployment](#post-deployment)

---

## 🔧 Preparación Local

### Paso 1: Instalar nuevas dependencias
```bash
pip install -r requirements.txt
```

### Paso 2: Generar SECRET_KEY segura
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copia el output y guárdalo para después.

### Paso 3: Crear archivo `.env` en la raíz del proyecto
```bash
cp .env.example .env
```

Edita `.env` y rellena:
```env
SECRET_KEY=tu-clave-generada-arriba
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Para PostgreSQL en Render (configurar después de crear DB)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=perfumeria_db
DB_USER=postgres
DB_PASSWORD=contraseña-segura
DB_HOST=dpg-xxxxx.postgres.render.com
DB_PORT=5432

STRIPE_SECRET_KEY=tu-stripe-live-key
STRIPE_PUBLIC_KEY=tu-stripe-public-key
```

### Paso 4: Prueba local
```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py check
```

---

## ⭐ Opción A: Render (Recomendado)

### Ventajas:
- ✅ Gratis para aplicaciones pequeñas (750h/mes)
- ✅ PostgreSQL gratis (400MB)
- ✅ Auto-deploy desde GitHub
- ✅ SSL automático
- ✅ Soporta WebSocket

### Pasos:

#### 1. Preparar repositorio GitHub
```bash
git init
git add .
git commit -m "Initial commit Aura Essence"
git remote add origin https://github.com/tu-usuario/aura-essence.git
git push -u origin main
```

#### 2. Crear cuenta en [Render.com](https://render.com)
- Inicia sesión con GitHub
- Conecta tu repositorio

#### 3. Crear PostgreSQL Database
1. Dashboard → New + → PostgreSQL
2. Nombre: `perfumeria-db`
3. Region: `US-East` (o cercana)
4. Plan: Free
5. Crear database
6. Copiar `External Database URL` (la necesitarás)

#### 4. Crear Web Service
1. Dashboard → New + → Web Service
2. Conectar tu repositorio GitHub
3. Nombre: `aura-essence-api`
4. Runtime: `Python 3`
5. Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input`
6. Start Command: `gunicorn myproject.wsgi`
7. Plan: Free

#### 5. Configurar Environment Variables (en Render)
Ir a: Settings → Environment
```
SECRET_KEY=tu-clave-generada
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=perfumeria_db
DB_USER=postgres
DB_PASSWORD=obtener-de-postgres
DB_HOST=obtener-de-postgres
DB_PORT=5432
STRIPE_SECRET_KEY=tu-stripe-live-key
STRIPE_PUBLIC_KEY=tu-stripe-public-key
CSRF_TRUSTED_ORIGINS=https://tu-app.onrender.com
```

#### 6. Deploy
- Render desplegará automáticamente al hacer push a `main`
- Esperar 5-10 minutos
- Visitar: `https://tu-app.onrender.com`

---

## 🐍 Opción B: PythonAnywhere

### Ventajas:
- ✅ Interfaz web amigable
- ✅ No requiere Git
- ✅ Bueno para principiantes

### Pasos:

#### 1. Crear cuenta en [PythonAnywhere.com](https://pythonanywhere.com)

#### 2. Subir archivos
1. Files → Upload a zip file
2. Sube tu proyecto comprimido
3. Descomprime en `/home/tuusuario/`

#### 3. Crear Virtual Environment
En Bash:
```bash
mkvirtualenv --python=/usr/bin/python3.10 aura-essence
pip install -r requirements.txt
```

#### 4. Configurar Django
Web → Add a new web app → Django
- Framework: Django 4.2
- Python 3.10
- Path: `/home/tuusuario/aura-essence/`

#### 5. Editar WSGI
Ir a: Web → WSGI file for [tu-dominio]
```python
import os
import sys

path = '/home/tuusuario/aura-essence'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 6. Configurar variables de entorno
```nano /home/tuusuario/.env```
```env
DEBUG=False
SECRET_KEY=tu-clave
ALLOWED_HOSTS=tuusuario.pythonanywhere.com
```

#### 7. Ejecutar migraciones
En Bash:
```bash
workon aura-essence
cd /home/tuusuario/aura-essence
python manage.py migrate
python manage.py collectstatic --no-input
```

#### 8. Reload
Web → Reload

---

## ✅ Post-Deployment

### 1. Verificar Migraciones
```bash
# Por SSH (Render/PythonAnywhere)
python manage.py migrate --list
```

### 2. Crear Superusuario
```bash
python manage.py createsuperuser --email admin@aura-essence.com --username admin
```

### 3. Verificar Static Files
```bash
# Debe mostrar sin errores 404
https://tu-dominio.com/static/css/index.css
https://tu-dominio.com/admin/
```

### 4. Configurar Stripe Webhooks
1. Ir a [Stripe Dashboard](https://dashboard.stripe.com)
2. Developers → Webhooks
3. Add endpoint: `https://tu-dominio.com/api/pago/webhook/`
4. Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
5. Copiar Signing secret → `.env` → `STRIPE_WEBHOOK_SECRET`

### 5. Verificar Logs
- **Render**: Logs → Live logs
- **PythonAnywhere**: Web → Error log, Server log

---

## 🔐 Checklist Seguridad Producción

- [ ] DEBUG = False
- [ ] SECRET_KEY es random y fuerte
- [ ] ALLOWED_HOSTS tiene solo dominio real
- [ ] CSRF_TRUSTED_ORIGINS configurado
- [ ] HTTPS activado (automático en Render)
- [ ] Variables de entorno en .env NO en settings.py
- [ ] Stripe keys son LIVE (no test)
- [ ] Base de datos configurada (PostgreSQL)
- [ ] Static files sirviendo correctamente
- [ ] Email configurado para notificaciones

---

## 🐛 Troubleshooting

### Error: "csrf verification failed"
**Solución**: Ir a settings.py y verificar:
```python
CSRF_TRUSTED_ORIGINS = ['https://tu-dominio.com']
```

### Error: "static files not found"
**Solución**:
```bash
python manage.py collectstatic --clear --no-input
```

### Error: "database connection refused"
**Solución**: Verificar en .env:
```bash
DB_HOST=dpg-xxxxxx.postgres.render.com  # NO localhost
```

### Error: "Module not found"
**Solución** (Render):
```bash
# Build command: debe tener pip install
pip install -r requirements.txt
```

---

## 📊 Monitoreo Recomendado

- Sentry (errores)
- New Relic (performance)
- Grafana (métricas)

Para MVP: Los logs de Render/PythonAnywhere son suficientes.

---

## 🎉 ¡LISTO!

Tu tienda **Aura Essence** está en la línea de fuego. 

Siguiente paso: **FASE 2 - Autenticación y Cuentas**
