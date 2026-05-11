from pathlib import Path
import os

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
        "orders.Pedido",
        "orders.DetallePedido",
        "orders.Carrito",
        "orders.ItemCarrito",
        "orders.Pago",
        "users.UserProfile",
        "users.EmailOTP",
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

        call_command("loaddata", str(fixture_path), verbosity=options.get("verbosity", 1))
        self.stdout.write(self.style.SUCCESS(f"Respaldo restaurado desde {fixture_path}"))

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