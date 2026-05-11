from pathlib import Path
import json
import os

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Exporta los registros existentes de la base de datos a un fixture JSON."

    excluded_models = {
        "admin.logentry",
        "auth.permission",
        "contenttypes.contenttype",
        "sessions.session",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=os.getenv("BACKUP_FILE_PATH", str(Path("backups") / "db_backup.json")),
            help="Ruta del archivo JSON de salida.",
        )
        parser.add_argument(
            "--fail-on-empty",
            action="store_true",
            help="Falla si no se encontraron registros exportables.",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fail_on_empty = options["fail_on_empty"]

        existing_tables = set(connection.introspection.table_names())
        objects = []
        exported_models = []
        skipped_models = []

        for model in sorted(apps.get_models(include_auto_created=False), key=lambda item: item._meta.label_lower):
            if not model._meta.managed or model._meta.proxy:
                continue

            model_label = model._meta.label_lower
            if model_label in self.excluded_models:
                skipped_models.append(model._meta.label)
                continue

            if model._meta.db_table not in existing_tables:
                skipped_models.append(model._meta.label)
                continue

            queryset = model.objects.all().order_by("pk")
            if not queryset.exists():
                continue

            serialized = serializers.serialize(
                "json",
                queryset,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
            )
            objects.extend(json.loads(serialized))
            exported_models.append(f"{model._meta.label} ({queryset.count()} registros)")

        if not objects:
            message = "No se encontraron registros exportables en la base de datos."
            if fail_on_empty:
                raise CommandError(message)

            self.stdout.write(self.style.WARNING(message))
            return

        with output_path.open("w", encoding="utf-8") as file_handle:
            json.dump(objects, file_handle, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Respaldo generado en {output_path}"))
        self.stdout.write(self.style.SUCCESS("Modelos exportados:"))
        for item in exported_models:
            self.stdout.write(f"- {item}")

        if skipped_models:
            self.stdout.write(self.style.WARNING("Modelos omitidos por no existir o por exclusión:"))
            for item in sorted(set(skipped_models)):
                self.stdout.write(f"- {item}")