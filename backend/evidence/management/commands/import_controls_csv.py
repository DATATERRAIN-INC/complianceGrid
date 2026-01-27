from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
import csv
import os
from evidence.models import EvidenceCategory, ReviewPeriod


class Command(BaseCommand):
    help = 'Import control categories from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing categories',
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create user accounts for assigned personnel if they do not exist',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return

        # Duration mapping - map CSV values to ReviewPeriod choices
        # Only accepts: Daily, Weekly, Monthly, Quarterly, Half Yearly, Annually (case-insensitive)
        duration_map = {
            'Daily': ReviewPeriod.DAILY,
            'daily': ReviewPeriod.DAILY,
            'Weekly': ReviewPeriod.WEEKLY,
            'weekly': ReviewPeriod.WEEKLY,
            'Monthly': ReviewPeriod.MONTHLY,
            'monthly': ReviewPeriod.MONTHLY,
            'Quarterly': ReviewPeriod.QUARTERLY,
            'quarterly': ReviewPeriod.QUARTERLY,
            'Half Yearly': ReviewPeriod.HALF_YEARLY_QUARTERLY,
            'half yearly': ReviewPeriod.HALF_YEARLY_QUARTERLY,
            'Annually': ReviewPeriod.ANNUALLY,
            'annually': ReviewPeriod.ANNUALLY,
        }

        created_count = 0
        updated_count = 0
        error_count = 0

        # Get default approver (Manoj)
        default_approver = None
        try:
            default_approver = User.objects.get(username='manoj')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING("User 'manoj' not found. Controls will be created without approver."))

        # Create or get users for assigned personnel
        user_map = {}
        if options['create_users']:
            user_names = ['Preeja', 'Karthi', 'Monisa', 'Manoj', 'Ajith', 'Vinoth', 'Murugesh', 'Mary', 'IT and Infra']
            for name in user_names:
                username = name.lower().replace(' ', '_')
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': f'{username}@company.com', 'first_name': name}
                )
                user_map[name] = user
                if created:
                    self.stdout.write(f"Created user: {name}")

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect delimiter, but default to comma
                sample = f.read(1024)
                f.seek(0)
                try:
                    sniffer = csv.Sniffer()
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    delimiter = ','
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                    try:
                        # Try different column name variations
                        name = row.get('Control Short') or row.get('Control') or row.get('Name') or row.get('Category') or ''
                        duration = row.get('Duration') or row.get('Review Period') or row.get('Period') or ''
                        to_do = row.get('To Do') or row.get('Description') or row.get('Requirements') or ''
                        evidence = row.get('Evidence') or row.get('Evidence Requirements') or ''
                        assigned_str = row.get('Assigned to') or row.get('Assigned') or ''
                        
                        if not name or not name.strip():
                            self.stdout.write(self.style.WARNING(f'Row {row_num}: Skipping - no name found'))
                            continue
                        
                        # Map duration - only accepts: Daily, Weekly, Monthly, Quarterly, Half Yearly, Annually
                        duration_clean = duration.strip() if duration else ''
                        review_period = ReviewPeriod.MONTHLY  # Default to Monthly
                        if duration_clean:
                            # Case-insensitive lookup - try exact match first, then lowercase
                            review_period = duration_map.get(duration_clean) or duration_map.get(duration_clean.lower()) or ReviewPeriod.MONTHLY
                        else:
                            # Empty duration defaults to Monthly
                            review_period = ReviewPeriod.MONTHLY
                        
                        # Combine description and evidence requirements
                        description = to_do.strip() if to_do else name
                        evidence_requirements = evidence.strip() if evidence else 'No specific requirements provided'
                        
                        # Create or update category
                        category, created = EvidenceCategory.objects.get_or_create(
                            name=name.strip(),
                            defaults={
                                'description': description,
                                'evidence_requirements': evidence_requirements,
                                'review_period': review_period,
                                'is_active': True,
                                'approver': default_approver,
                            }
                        )
                        
                        # Set approver to Manoj if not already set (for existing categories)
                        if not created and not category.approver and default_approver:
                            category.approver = default_approver
                            category.save()
                        
                        # Update assignee if provided
                        if assigned_str and assigned_str.strip():
                            assigned_name = assigned_str.strip()
                            # Try to find user by first name, last name, or username
                            assigned_user = None
                            
                            # Try exact username match first
                            try:
                                assigned_user = User.objects.get(username__iexact=assigned_name.lower().replace(' ', '_'))
                            except User.DoesNotExist:
                                # Try first name match
                                try:
                                    assigned_user = User.objects.get(first_name__iexact=assigned_name)
                                except (User.DoesNotExist, User.MultipleObjectsReturned):
                                    # Try partial match on first name
                                    users = User.objects.filter(first_name__icontains=assigned_name.split()[0] if assigned_name.split() else assigned_name)
                                    if users.count() == 1:
                                        assigned_user = users.first()
                            
                            if assigned_user:
                                category.assignee = assigned_user
                                category.save()
                                if created:
                                    self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Created - {category.name} (Assigned to {assigned_user.username})'))
                                else:
                                    self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Updated - {category.name} (Assigned to {assigned_user.username})'))
                            else:
                                if created:
                                    created_count += 1
                                    self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Created - {category.name} (Assignee "{assigned_name}" not found)'))
                                else:
                                    updated_count += 1
                                    self.stdout.write(self.style.WARNING(f'Row {row_num}: Already exists - {category.name} (Assignee "{assigned_name}" not found)'))
                        else:
                            if created:
                                created_count += 1
                                self.stdout.write(self.style.SUCCESS(f'Row {row_num}: Created - {category.name}'))
                            else:
                                updated_count += 1
                                self.stdout.write(self.style.WARNING(f'Row {row_num}: Already exists - {category.name}'))
                            
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'Row {row_num}: Error - {str(e)}'))
                        continue

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete: {created_count} created, {updated_count} already existed, {error_count} errors'
        ))

