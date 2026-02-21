# Documentación Completa del Proyecto Aura Essence

## 🌟 Introducción
Aura Essence es una plataforma de e-commerce de perfumería de lujo desarrollada con Django y Django REST Framework. Este documento consolida toda la información necesaria para configurar, desarrollar y desplegar la aplicación.

---

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.10+
- Git
- PostgreSQL (opcional para desarrollo, requerido para producción)

### Instalación Local

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/adaldean/Perfumes.git
    cd Perfumes
    ```

2.  **Configurar entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/Mac
    # .venv\Scripts\activate   # Windows
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz (puedes usar `.env.example` como base).
    ```env
    DEBUG=True
    SECRET_KEY=tu_clave_secreta_local
    ALLOWED_HOSTS=localhost,127.0.0.1
    STRIPE_PUBLIC_KEY=pk_test_...
    STRIPE_SECRET_KEY=sk_test_...
    ```

5.  **Base de Datos y Migraciones:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    ```

6.  **Ejecutar servidor:**
    ```bash
    python manage.py runserver
    ```
    Visita `http://127.0.0.1:8000/`.

---

## 📚 API Rest

La API está disponible en `/api/`.

### Autenticación
Usa JWT (JSON Web Tokens).
- **Login:** POST `/api/auth/login/`
  - Body: `{"username": "user", "password": "pass"}`
  - Response: `{"access": "...", "refresh": "..."}`

### Endpoints Principales
- **Productos:** GET `/api/productos/`
- **Carrito:** GET/POST `/api/carrito/`
- **Pedidos:** GET/POST `/api/pedidos/`

---

## ☁️ Despliegue en Render

El proyecto está pre-configurado para desplegarse en [Render](https://render.com).

### Configuración Automática (Blueprint)
El repositorio incluye un archivo `render.yaml`.
1. En el dashboard de Render, selecciona **"New" > "Blueprint"**.
2. Conecta tu repositorio de GitHub.
3. Render detectará la configuración y creará el servicio web y la base de datos PostgreSQL automáticamente.

### Configuración Manual
Si prefieres hacerlo manualmente:

1. **Crear Web Service:**
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input`
   - **Start Command:** `python manage.py migrate --noinput && gunicorn myproject.wsgi:application`

2. **Variables de Entorno (Environment Variables):**
   - `PYTHON_VERSION`: `3.11.8`
   - `SECRET_KEY`: (Genera una segura)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (o tu dominio `.onrender.com`)
   - `DATABASE_URL`: (Render la provee automáticamente si añades una base de datos)
   - `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY`: Tus claves de Stripe.

---

## 💳 Pagos con Stripe
El proyecto utiliza Stripe para procesar pagos.
1. Configura tus claves en `.env` o en las variables de entorno de Render.
2. Webhooks: Configura el endpoint `/api/webhook/stripe/` en para recibir eventos de pago.

---

## 🛠 Estructura del Proyecto
- `apps/api/`: Contiene la lógica principal, modelos y vistas.
- `myproject/settings.py`: Configuración global (adaptada para `dj-database-url`).
- `templates/`: Plantillas HTML con Tailwind CSS.
- `static/`: Archivos CSS/JS compilados.

