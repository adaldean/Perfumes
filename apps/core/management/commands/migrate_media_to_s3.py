"""
Management command to migrate media files from local storage to AWS S3.
Runs automatically on deployment when S3 credentials are configured.
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage


class Command(BaseCommand):
    help = 'Migrate media files from local directory to AWS S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show files that would be migrated without actually migrating them',
        )

    def handle(self, *args, **options):
        # Check if S3 is configured
        if not os.getenv('AWS_ACCESS_KEY_ID'):
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  AWS_ACCESS_KEY_ID not configured. Skipping S3 migration.'
                )
            )
            return

        # Get local media path
        local_media_root = settings.MEDIA_ROOT
        
        if not os.path.exists(local_media_root):
            self.stdout.write(
                self.style.WARNING(
                    f'📁 No local media directory found at {local_media_root}. Nothing to migrate.'
                )
            )
            return

        # Count files to migrate
        files_to_migrate = []
        for root, dirs, files in os.walk(local_media_root):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path for S3
                rel_path = os.path.relpath(file_path, local_media_root)
                files_to_migrate.append((file_path, rel_path))

        if not files_to_migrate:
            self.stdout.write(
                self.style.SUCCESS('✅ No media files to migrate.')
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f'🔄 Found {len(files_to_migrate)} file(s) to migrate to S3...\n'
            )
        )

        if options['dry_run']:
            self.stdout.write(self.style.NOTICE('📋 DRY RUN - No files will be uploaded\n'))

        # Migrate files
        success_count = 0
        error_count = 0

        for local_path, s3_key in files_to_migrate:
            try:
                if options['dry_run']:
                    self.stdout.write(f'  → {s3_key}')
                else:
                    # Upload to S3
                    with open(local_path, 'rb') as f:
                        default_storage.save(s3_key, f)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {s3_key}')
                    )
                success_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {s3_key}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        if options['dry_run']:
            self.stdout.write(
                self.style.NOTICE(
                    f'📋 DRY RUN COMPLETE: {success_count} file(s) would be migrated'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Migration complete: {success_count} file(s) migrated'
                )
            )
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {error_count} file(s) failed')
                )
