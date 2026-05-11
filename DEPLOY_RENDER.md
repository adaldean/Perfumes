# Despliegue en Render y migración a PostgreSQL

Resumen rápido:
- El proyecto usa `dj_database_url` y, si existe `DATABASE_URL`, Django usará la DB indicada.
- En Render debes añadir variables de entorno (Environment) para que la app use Postgres y claves seguras.

Variables obligatorias a configurar en Render (Dashboard → Environment → Environment Variables):
- `DATABASE_URL` = postgresql://user:password@host:5432/dbname
- `SECRET_KEY` = cadena segura
- `DEBUG` = False

**Almacenamiento de Imágenes (Media):**
Render borra archivos locales al reiniciar. Configura Cloudinary:
- `CLOUDINARY_CLOUD_NAME` = tu_nombre_de_cloud
- `CLOUDINARY_API_KEY` = tu_api_key
- `CLOUDINARY_API_SECRET` = tu_api_secret

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

Pasos para respaldar y restaurar datos en PostgreSQL sin perder registros:
1. En local o en un entorno con la base viva, genera el respaldo JSON semilla:
   ```bash
   python manage.py backup_database --output backups/db_backup.json
   ```
2. En Render se monta un disco persistente en `/var/data` y el backup real del entorno se guarda ahí.
3. En Render, el flujo automático hace esto:
   ```bash
   preDeployCommand -> python manage.py backup_database --output /var/data/backups/db_backup.json
   startCommand -> python manage.py migrate --noinput && python manage.py create_initial_users && python manage.py restore_database --fixture /var/data/backups/db_backup.json && python manage.py backup_database --output /var/data/backups/db_backup.json && gunicorn myproject.wsgi:application
   ```
4. Si la base llega a borrarse o quedar vacía, el arranque toma primero el backup del disco persistente. Si no existe todavía, usa el fixture semilla del repositorio.
5. Si necesitas forzar una restauración manual en una base vacía o de prueba:
   ```bash
   python manage.py restore_database --fixture backups/db_backup.json --force
   ```

Notas y recomendaciones:
- El respaldo omite tablas técnicas de Django como `contenttypes`, `auth.permission`, `sessions` y `admin.logentry` para evitar conflictos al restaurar.
- El comando de respaldo salta tablas que no existan en la base activa y no rompe el despliegue si la base todavía está vacía.
- El respaldo no incluye archivos de `media/`; si necesitas imágenes, debes respaldar `media/` o moverlos a almacenamiento externo.
- Mantén `DATABASE_URL` y las claves secretas solo en Render, no en el repositorio.
- Si quieres respaldo continuo fuera de los despliegues, el siguiente paso correcto es añadir un cron job que suba el JSON a un storage externo como S3. Render cron jobs no pueden usar disco persistente.

Verificación post-migración:
- Inicia servidor local apuntando a la Postgres remota y revisa que usuarios, productos y pedidos estén presentes.
- Corre `python manage.py check` y algunas consultas en admin.
