# Despliegue en Render y migración a PostgreSQL

Resumen rápido:
- El proyecto usa `dj_database_url` y, si existe `DATABASE_URL`, Django usará la DB indicada.
- En Render debes añadir variables de entorno (Environment) para que la app use Postgres y claves seguras.

Variables obligatorias a configurar en Render (Dashboard → Environment → Environment Variables):
- `DATABASE_URL` = postgresql://user:password@host:5432/dbname
- `SECRET_KEY` = cadena segura
- `DEBUG` = False

Variables opcionales pero recomendadas:
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLIC_KEY`, `STRIPE_WEBHOOK_SECRET`
- `MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_PUBLIC_KEY`
- `ALLOWED_HOSTS` = perfumes-1.onrender.com (o tu dominio)

Comandos en Render (Build & Start):
- Build command (ejemplo usado por Render):
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --no-input
  ```
- Start command (arranque):
  ```bash
  python manage.py migrate --noinput && gunicorn myproject.wsgi:application
  ```

Pasos para migrar datos sin pérdidas desde SQLite local a Postgres (ideal cuando ya tienes Postgres en Render o en hosting):
1. En tu máquina local, commitea todos los cambios actuales.
2. Genera un volcado JSON de los datos actuales (se crea `data_dump.json`):
   ```bash
   ./scripts/migrate_sqlite_to_postgres.sh --dump
   ```
3. Crea la base Postgres (ej. en Render crea el servicio Managed Postgres o configúrala en tu proveedor).
4. Exporta la URL de conexión (no la pongas en el repo):
   ```bash
   export DATABASE_URL=postgres://usuario:contraseña@host:5432/nombredb
   ```
5. Ejecuta migraciones y carga los datos:
   ```bash
   ./scripts/migrate_sqlite_to_postgres.sh --migrate
   ```

Notas y recomendaciones:
- El volcado excluye `contenttypes` y `auth.permission` para evitar colisiones; Django recreará las tablas necesarias con `migrate`.
- Revisa `data_dump.json` si hay modelos con datos binarios especiales (el media no se exporta con dumpdata). Debes copiar manualmente los archivos de `media/` si usas almacenamiento en la nube.
- En Render debes añadir las variables del panel de Environment; nunca subas `.env` con secretos.
- Asegúrate de que `psycopg2-binary` está en `requirements.txt` (ya está). Si no, añádelo.

Verificación post-migración:
- Inicia servidor local apuntando a la Postgres remota y revisa que usuarios, productos y pedidos estén presentes.
- Corre `python manage.py check` y algunas consultas en admin.
