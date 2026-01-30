"""
Single management command that:
1. Clears all submission history (EvidenceSubmission and related)
2. Removes local document files (evidence_files directory)
3. Updates users from hardcoded list (same as update_users)
4. Refreshes/imports controls from all_categories.csv (Control Short, Duration, To Do, Evidence, Assigned to)
5. Sets default approver (Manoj) for all controls

Usage:
  python manage.py full_refresh
  python manage.py full_refresh --csv path/to/all_categories.csv
  python manage.py full_refresh --dry-run   # show what would be done, no destructive changes
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
import csv
import os
import shutil

from evidence.models import (
    EvidenceCategory,
    EvidenceSubmission,
    EvidenceFile,
    ReviewPeriod,
)


# Same user list as update_users
USERS_TO_KEEP = [
    {'username': 'sakthi', 'email': 'sakthi@dataterrain.com', 'first_name': 'Sakthi', 'last_name': 'C'},
    {'username': 'monisa', 'email': 'monisa@dataterrain.com', 'first_name': 'Monisa', 'last_name': 'V'},
    {'username': 'manoj', 'email': 'manoj@dataterrain.com', 'first_name': 'Manoj', 'last_name': 'M'},
    {'username': 'preeja', 'email': 'preeja@dataterrain.com', 'first_name': 'Preeja', 'last_name': 'P'},
    {'username': 'murugesh', 'email': 'murugesh@dataterrain.com', 'first_name': 'Murugesh', 'last_name': 'C'},
    {'username': 'vinothkumar', 'email': 'vinothkumar@dataterrain.com', 'first_name': 'Vinoth Kumar', 'last_name': 'R'},
    {'username': 'ajithkumar', 'email': 'ajithkumar@dataterrain.com', 'first_name': 'Ajith Kumar', 'last_name': 'H'},
    {'username': 'karthikeyan', 'email': 'karthikeyanchandrakumar@dataterrain.com', 'first_name': 'Karthikeyan', 'last_name': 'C'},
    {'username': 'mary', 'email': 'mary@dataterrain.com', 'first_name': 'Mary', 'last_name': 'M'},
]

# Only these 6 duration values are supported. Any other CSV value → review_period = null.
DURATION_MAP = {
    'Daily': ReviewPeriod.DAILY,
    'daily': ReviewPeriod.DAILY,
    'Weekly': ReviewPeriod.WEEKLY,
    'weekly': ReviewPeriod.WEEKLY,
    'Monthly': ReviewPeriod.MONTHLY,
    'monthly': ReviewPeriod.MONTHLY,
    'Quarterly': ReviewPeriod.QUARTERLY,
    'quarterly': ReviewPeriod.QUARTERLY,
    'Half yearly': ReviewPeriod.HALF_YEARLY_QUARTERLY,
    'half yearly': ReviewPeriod.HALF_YEARLY_QUARTERLY,
    'Half Yearly': ReviewPeriod.HALF_YEARLY_QUARTERLY,
    'Annually': ReviewPeriod.ANNUALLY,
    'annually': ReviewPeriod.ANNUALLY,
}


def find_user_by_assignee_name(assigned_str):
    """Resolve 'Assigned to' string to User (first_name or username)."""
    if not assigned_str or not assigned_str.strip():
        return None
    name = assigned_str.strip()
    try:
        return User.objects.get(username__iexact=name.lower().replace(' ', '_'))
    except User.DoesNotExist:
        pass
    try:
        return User.objects.get(first_name__iexact=name)
    except (User.DoesNotExist, User.MultipleObjectsReturned):
        pass
    users = User.objects.filter(first_name__icontains=name.split()[0] if name.split() else name)
    if users.count() == 1:
        return users.first()
    # Try "Vinoth Kumar" -> vinothkumar, "Ajith Kumar" -> ajithkumar, etc.
    un = name.lower().replace(' ', '')  # vinothkumar
    for u in User.objects.all():
        if u.username.lower() == un or (u.first_name and u.first_name.lower().replace(' ', '') == un):
            return u
    return None


class Command(BaseCommand):
    help = (
        'Clear submission history, remove local documents, update users, '
        'import/refresh controls from all_categories.csv, set default approver'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default=None,
            help='Path to CSV (default: all_categories.csv in project backend directory)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only report what would be done; no destructive changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        csv_path = options['csv']
        if not csv_path:
            csv_path = os.path.join(settings.BASE_DIR, 'all_categories.csv')
        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] No changes will be made.'))

        # 1. Clear submission history
        count = EvidenceSubmission.objects.count()
        if count:
            if dry_run:
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Would delete {count} submission(s).'))
            else:
                EvidenceSubmission.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'Cleared {count} submission(s).'))
        else:
            self.stdout.write('No submissions to clear.')

        # 2. Remove local documents
        media_root = settings.MEDIA_ROOT
        evidence_dir = os.path.join(media_root, 'evidence_files')
        if os.path.exists(evidence_dir):
            if dry_run:
                n = sum(len(files) for _, _, files in os.walk(evidence_dir))
                self.stdout.write(self.style.WARNING(f'[DRY RUN] Would remove {n} file(s) from {evidence_dir}'))
            else:
                try:
                    shutil.rmtree(evidence_dir)
                    self.stdout.write(self.style.SUCCESS(f'Removed local documents: {evidence_dir}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error removing evidence_files: {e}'))
        else:
            self.stdout.write('No evidence_files directory found.')

        # 3. Update users
        keep_emails = {u['email'] for u in USERS_TO_KEEP}
        keep_usernames = {u['username'] for u in USERS_TO_KEEP}
        if not dry_run:
            for u in USERS_TO_KEEP:
                user, created = User.objects.get_or_create(
                    username=u['username'],
                    defaults={
                        'email': u['email'],
                        'first_name': u['first_name'],
                        'last_name': u['last_name'],
                    },
                )
                if not created:
                    user.email = u['email']
                    user.first_name = u['first_name']
                    user.last_name = u['last_name']
                    user.set_password('Data@123')
                    user.save()
                else:
                    user.set_password('Data@123')
                    user.save()
            other = User.objects.exclude(email__in=keep_emails).exclude(username__in=keep_usernames)
            other_ids = list(other.values_list('id', flat=True))
            if other_ids:
                EvidenceCategory.objects.filter(assignee_id__in=other_ids).update(assignee=None)
                EvidenceCategory.objects.filter(approver_id__in=other_ids).update(approver=None)
                other.delete()
        self.stdout.write(self.style.SUCCESS(f'Users updated: {len(USERS_TO_KEEP)} kept/synced.'))

        # 4. Import/refresh controls from CSV
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV not found: {csv_path}'))
            return
        default_approver = None
        if not dry_run:
            try:
                default_approver = User.objects.get(username='manoj')
            except User.DoesNotExist:
                pass
        created_count = 0
        updated_count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                f.seek(0)
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                except Exception:
                    delimiter = ','
                reader = csv.DictReader(f, delimiter=delimiter)
                for row_num, row in enumerate(reader, start=2):
                    name = (row.get('Control Short') or row.get('Control') or row.get('Name') or row.get('Category') or '').strip()
                    if not name:
                        continue
                    duration_str = (row.get('Duration') or '').strip()
                    to_do = (row.get('To Do') or '').strip() or name
                    evidence = (row.get('Evidence') or '').strip() or 'No specific requirements provided'
                    assigned_str = (row.get('Assigned to') or row.get('Assigned') or '').strip()
                    # Only the 6 allowed values; any other → null
                    review_period = None
                    if duration_str:
                        review_period = DURATION_MAP.get(duration_str) or DURATION_MAP.get(duration_str.strip().lower())
                    assignee = None
                    if assigned_str and not dry_run:
                        assignee = find_user_by_assignee_name(assigned_str)
                    if dry_run:
                        if EvidenceCategory.objects.filter(name=name).exists():
                            updated_count += 1
                        else:
                            created_count += 1
                        continue
                    defaults = {
                        'description': to_do,
                        'evidence_requirements': evidence,
                        'is_active': True,
                        'approver': default_approver,
                        'assignee': assignee,
                    }
                    if review_period is not None:
                        defaults['review_period'] = review_period
                    category, created = EvidenceCategory.objects.get_or_create(name=name, defaults=defaults)
                    if created:
                        created_count += 1
                    else:
                        category.description = to_do
                        category.evidence_requirements = evidence
                        category.review_period = review_period
                        category.assignee = assignee
                        if not category.approver and default_approver:
                            category.approver = default_approver
                        category.save()
                        updated_count += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV: {e}'))
            return
        self.stdout.write(self.style.SUCCESS(f'Controls: {created_count} created, {updated_count} updated from CSV.'))

        # 5. Set default approver for any controls still without one
        if not dry_run and default_approver:
            updated = EvidenceCategory.objects.filter(is_active=True, approver__isnull=True).update(approver=default_approver)
            if updated:
                self.stdout.write(self.style.SUCCESS(f'Set default approver (Manoj) on {updated} control(s).'))
        elif dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] Would set default approver (Manoj) where missing.'))

        self.stdout.write(self.style.SUCCESS('Full refresh complete.'))
