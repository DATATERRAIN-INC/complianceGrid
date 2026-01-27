from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evidence.models import EvidenceCategory


class Command(BaseCommand):
    help = 'Set Manoj as the default approver for all controls that do not have an approver'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all controls, even if they already have an approver',
        )

    def handle(self, *args, **options):
        # Get Manoj user
        try:
            approver = User.objects.get(username='manoj')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'manoj' not found. Please create the user first."))
            return

        # Get controls without approver
        if options['force']:
            controls = EvidenceCategory.objects.filter(is_active=True)
            self.stdout.write(f"Force updating all {controls.count()} active controls...")
        else:
            controls = EvidenceCategory.objects.filter(is_active=True, approver__isnull=True)
            self.stdout.write(f"Found {controls.count()} active controls without approver...")

        updated_count = 0
        for control in controls:
            if options['force'] or not control.approver:
                control.approver = approver
                control.save()
                updated_count += 1

        if updated_count > 0:
            self.stdout.write(self.style.SUCCESS(
                f'[SUCCESS] Updated {updated_count} control(s) with approver: {approver.username} ({approver.first_name})'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('No controls needed updating.'))
