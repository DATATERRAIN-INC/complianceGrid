from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from evidence.models import EvidenceFile


class Command(BaseCommand):
    help = 'Remove all local document files from the media directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-records',
            action='store_true',
            help='Keep database records but remove file references (default: False - removes files only)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        keep_records = options['keep_records']
        dry_run = options['dry_run']
        
        media_root = settings.MEDIA_ROOT
        evidence_files_dir = os.path.join(media_root, 'evidence_files')
        
        if not os.path.exists(evidence_files_dir):
            self.stdout.write(self.style.WARNING('No evidence_files directory found. Nothing to delete.'))
            return
        
        # Count files before deletion
        file_count = 0
        total_size = 0
        
        for root, dirs, files in os.walk(evidence_files_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    pass
        
        if file_count == 0:
            self.stdout.write(self.style.WARNING('No files found in evidence_files directory.'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would delete {file_count} file(s) ({total_size / (1024*1024):.2f} MB)'))
            self.stdout.write(f'[DRY RUN] Files location: {evidence_files_dir}')
            return
        
        # Confirm deletion
        self.stdout.write(f'Found {file_count} file(s) ({total_size / (1024*1024):.2f} MB) in {evidence_files_dir}')
        self.stdout.write(self.style.WARNING('This will permanently delete all local document files.'))
        
        # Delete the entire evidence_files directory
        try:
            shutil.rmtree(evidence_files_dir)
            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Deleted {file_count} file(s) from {evidence_files_dir}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting files: {str(e)}'))
            return
        
        # Optionally update database records
        if keep_records:
            # Clear file field but keep records
            updated = EvidenceFile.objects.filter(file__isnull=False).update(file=None)
            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Cleared file references from {updated} database records'))
        else:
            # Just remove files, keep database records with file field intact
            # (Files will be missing but records remain)
            self.stdout.write(self.style.SUCCESS('Database records kept. File fields may reference non-existent files.'))
