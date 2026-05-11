from pathlib import Path
import json
import os
import tempfile

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restaura un fixture JSON si la base no tiene datos de negocio."

    check_models = (
        "catalog.Marca",
        "catalog.Categoria",
        "catalog.Producto",
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=os.getenv("BACKUP_FILE_PATH", str(Path("backups") / "db_backup.json")),
            help="Ruta del fixture JSON a restaurar.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Restaura aunque ya existan datos de negocio.",
        )

    def handle(self, *args, **options):
        fixture_path = Path(options["fixture"])
        force = options["force"]
        fallback_path = settings.BASE_DIR / "backups" / fixture_path.name

        if not fixture_path.exists() and fallback_path.exists():
            fixture_path = fallback_path

        if not fixture_path.exists():
            raise CommandError(f"No se encontró el fixture de respaldo: {fixture_path}")

        if not force and self.database_has_business_data():
            self.stdout.write(self.style.WARNING("La base ya tiene datos de negocio. Se omite la restauración."))
            return

        filtered_fixture_path = self._build_catalog_fixture_file(fixture_path)
        call_command("loaddata", str(filtered_fixture_path), verbosity=options.get("verbosity", 1))
        self.stdout.write(self.style.SUCCESS(f"Catálogo restaurado desde {fixture_path}"))

    def database_has_business_data(self):
        for model_label in self.check_models:
            model = apps.get_model(model_label)
            if model is None:
                continue

            if model._meta.db_table not in self._existing_tables():
                continue

            if model.objects.exists():
                return True

        return False

    def _existing_tables(self):
        if not hasattr(self, "_tables_cache"):
            from django.db import connection

            self._tables_cache = set(connection.introspection.table_names())

        return self._tables_cache

    def _build_catalog_fixture_file(self, fixture_path):
        with fixture_path.open("r", encoding="utf-8") as fixture_file:
            data = json.load(fixture_file)

        catalog_data = [item for item in data if item.get("model", "").startswith("catalog.")]
        if not catalog_data:
            raise CommandError("El fixture no contiene registros de catálogo para restaurar.")

        tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        with tmp_file:
            json.dump(catalog_data, tmp_file, ensure_ascii=False, indent=2)

        return Path(tmp_file.name)