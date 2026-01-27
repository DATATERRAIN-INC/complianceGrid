from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evidence.models import EvidenceCategory, ReviewPeriod, CategoryGroup


class Command(BaseCommand):
    help = 'Add a new control under Security category group'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Control name')
        parser.add_argument('--group', type=str, required=True, 
                          choices=['ACCESS_CONTROLS', 'NETWORK_SECURITY', 'PHYSICAL_SECURITY', 
                                  'DATA_PROTECTION', 'ENDPOINT_SECURITY', 'MONITORING_INCIDENT'],
                          help='Security sub-group')
        parser.add_argument('--duration', type=str, required=True,
                          choices=['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Half Yearly', 'Annually'],
                          help='Review period duration')
        parser.add_argument('--description', type=str, default='', help='Control description')
        parser.add_argument('--evidence', type=str, default='No specific requirements provided', 
                          help='Evidence requirements')
        parser.add_argument('--assignee', type=str, default=None, 
                          help='Username of person assigned to this control')

    def handle(self, *args, **options):
        name = options['name']
        group_code = options['group']
        duration = options['duration']
        description = options['description'] or name
        evidence = options['evidence']
        assignee_username = options['assignee']

        # Duration mapping
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

        review_period = duration_map.get(duration) or duration_map.get(duration.lower()) or ReviewPeriod.MONTHLY
        category_group = getattr(CategoryGroup, group_code, CategoryGroup.UNCATEGORIZED)

        # Get assignee if provided
        assignee = None
        if assignee_username:
            try:
                assignee = User.objects.get(username=assignee_username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"User '{assignee_username}' not found. Creating control without assignee."))

        # Get default approver (Manoj)
        approver = None
        try:
            approver = User.objects.get(username='manoj')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING("User 'manoj' not found. Creating control without approver."))

        # Create the control
        category, created = EvidenceCategory.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'evidence_requirements': evidence,
                'review_period': review_period,
                'category_group': category_group,
                'is_active': True,
                'assignee': assignee,
                'approver': approver,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Successfully created control: {name}'))
            self.stdout.write(f'  - Group: {category_group.label}')
            self.stdout.write(f'  - Duration: {review_period.label}')
            if assignee:
                self.stdout.write(f'  - Assigned to: {assignee.username}')
        else:
            self.stdout.write(self.style.WARNING(f'Control "{name}" already exists. Updating...'))
            category.description = description
            category.evidence_requirements = evidence
            category.review_period = review_period
            category.category_group = category_group
            if assignee:
                category.assignee = assignee
            # Set approver to Manoj if not already set
            if not category.approver and approver:
                category.approver = approver
            category.save()
            self.stdout.write(self.style.SUCCESS(f'[SUCCESS] Successfully updated control: {name}'))
            if approver:
                self.stdout.write(f'  - Approver: {approver.username}')
