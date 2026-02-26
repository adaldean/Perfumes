#!/usr/bin/env bash
set -euo pipefail

# Script seguro para migrar datos de SQLite (db.sqlite3) a PostgreSQL
# Uso:
# 1. Revisa y commitea cambios: git status
# 2. Crea respaldo local (este script hace respaldo automático a data_dump.json)
# 3. Exporta datos: ./scripts/migrate_sqlite_to_postgres.sh --dump
# 4. Define la conexión Postgres en DATABASE_URL (o export NEW_DATABASE_URL)
# 5. Ejecuta el script para migrar: ./scripts/migrate_sqlite_to_postgres.sh --migrate

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_ACTIVATE="${PROJECT_DIR}/.venv/bin/activate"

if [ ! -f "${PROJECT_DIR}/manage.py" ]; then
  echo "Ejecuta este script desde la raíz del proyecto (donde está manage.py)." >&2
  exit 1
fi

if [ -f "${VENV_ACTIVATE}" ]; then
  # shellcheck disable=SC1090
  source "${VENV_ACTIVATE}"
fi

DATAFILE="${PROJECT_DIR}/data_dump.json"

function dumpdata() {
  echo "Creando volcado de datos desde SQLite a ${DATAFILE}..."
  python manage.py dumpdata --natural-primary --natural-foreign -e contenttypes -e auth.permission --indent 2 > "${DATAFILE}"
  echo "Volcado creado: ${DATAFILE}"
}

function migrate_to_postgres() {
  # Prefer NEW_DATABASE_URL si está definida
  DBURL="${NEW_DATABASE_URL:-${DATABASE_URL:-}}"
  if [ -z "$DBURL" ]; then
    echo "ERROR: No se ha definido DATABASE_URL ni NEW_DATABASE_URL. Exporta DATABASE_URL con la cadena de conexión Postgres." >&2
    echo "Ejemplo: export DATABASE_URL=postgres://user:pass@host:5432/dbname" >&2
    exit 1
  fi

  echo "Usando DATABASE_URL=(oculta)"

  # Ejecutar migraciones en la base Postgres
  echo "Ejecutando migraciones en la base Postgres..."
  export DATABASE_URL="$DBURL"
  python manage.py migrate --noinput

  if [ ! -f "${DATAFILE}" ]; then
    echo "No se encontró ${DATAFILE}. Ejecuta --dump primero o crea data_dump.json manualmente." >&2
    exit 1
  fi

  echo "Cargando datos desde ${DATAFILE} en Postgres..."
  python manage.py loaddata "${DATAFILE}"
  echo "Importación completada. Verifica la app y corre pruebas." 
}

if [ "${1:-}" = "--dump" ]; then
  dumpdata
  exit 0
fi

if [ "${1:-}" = "--migrate" ]; then
  migrate_to_postgres
  exit 0
fi

cat <<'USAGE'
Uso: scripts/migrate_sqlite_to_postgres.sh [--dump|--migrate]

--dump    : Exporta datos de la base actual a data_dump.json (excluye contenttypes y auth.permission)
--migrate : Ejecuta migraciones en la base Postgres configurada en DATABASE_URL y carga data_dump.json

Flujo recomendado:
  1) git commit -a -m "Antes de migrar: respaldo"
  2) ./scripts/migrate_sqlite_to_postgres.sh --dump
  3) export DATABASE_URL=postgres://user:pass@host:5432/dbname
  4) ./scripts/migrate_sqlite_to_postgres.sh --migrate

Nota: No dejes credenciales en texto plano en repositorio. Usa el panel de variables del servicio (Render) o un secreto.
USAGE
