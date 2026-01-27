from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evidence.models import EvidenceCategory


class Command(BaseCommand):
    help = 'Update assignees for specific controls'

    def handle(self, *args, **options):
        # Control and assignee mapping
        controls_data = [
            {'name': 'Code of Conduct', 'assignee': 'Preeja'},
            {'name': 'Complaints and Feedback', 'assignee': 'Preeja'},
            {'name': 'CISO Responsibilities', 'assignee': 'Preeja'},
            {'name': 'Training Calendar', 'assignee': 'Preeja'},
            {'name': 'Network Diagram', 'assignee': 'Murugesh'},
            {'name': 'Client Escalation matrix', 'assignee': 'Manoj'},
            {'name': 'Risk Management Policy', 'assignee': 'Karthikeyan'},
            {'name': 'Ratings of risks', 'assignee': 'Karthikeyan'},
            {'name': 'Privacy in risk register', 'assignee': 'Karthikeyan'},
            {'name': 'Segregration of duties', 'assignee': 'Preeja'},
            {'name': 'Cloud infrastructure', 'assignee': 'Murugesh'},
            {'name': 'Endpoint protection for WFH Staff', 'assignee': 'Ajith'},
            {'name': 'Active Directory', 'assignee': 'Ajith'},
            {'name': 'Userid for non AD accounts', 'assignee': 'Ajith'},
            {'name': 'IAM on cloud infra', 'assignee': 'Vinoth'},
            {'name': 'ssh access for cloud', 'assignee': 'Vinoth'},
            {'name': 'Software list', 'assignee': 'Ajith'},
            {'name': 'Password policy in AD', 'assignee': 'Ajith'},
            {'name': 'Domain Controller / AD', 'assignee': 'Ajith'},
            {'name': 'Privileged access is restricted', 'assignee': 'Ajith'},
            {'name': 'No access to non employees', 'assignee': 'Preeja'},
            {'name': 'Role based access', 'assignee': 'Ajith'},
            {'name': 'Role based access - cloud', 'assignee': 'Murugesh'},
            {'name': 'Office Entry is restricted', 'assignee': 'Mary'},
            {'name': 'CCTV', 'assignee': 'Mary'},
            {'name': 'Security Guard', 'assignee': 'Mary'},
            {'name': 'Visitor Badges', 'assignee': 'Mary'},
            {'name': 'Visitor Escorting', 'assignee': 'Mary'},
            {'name': 'Employee picture ID cards', 'assignee': 'Mary'},
            {'name': 'Sharing of badges', 'assignee': 'Mary'},
            {'name': 'cloud firewall', 'assignee': 'Vinoth'},
            {'name': 'Whitelisted incoming traffic', 'assignee': 'Ajith'},
            {'name': 'Content-Filtering', 'assignee': 'Ajith'},
            {'name': 'No printer Access', 'assignee': 'Mary'},
            {'name': 'Removable media prohibited', 'assignee': 'Ajith'},
            {'name': 'SSH / SSL connection to Cloud environment', 'assignee': 'Murugesh'},
            {'name': 'SSL connections for cloud hosted applications.', 'assignee': 'Vinoth'},
            {'name': 'Incident ticket details captured', 'assignee': 'Preeja'},
            {'name': 'Software code on GIT/SVN', 'assignee': 'Monisa'},
            {'name': 'QA testing / UAT Testing', 'assignee': 'Monisa'},
            {'name': 'Separate environment for changes', 'assignee': 'Murugesh'},
            {'name': 'Testing data is masked', 'assignee': 'Monisa'},
            {'name': 'UPS, DG', 'assignee': 'Mary'},
            {'name': 'ISP redundancy', 'assignee': 'Ajith'},
        ]

        updated_count = 0
        not_found_count = 0
        assignee_not_found_count = 0

        for control_data in controls_data:
            control_name = control_data['name']
            assignee_name = control_data['assignee']

            # Find control by name (case-insensitive, flexible matching)
            try:
                # Try exact match first
                control = EvidenceCategory.objects.get(name__iexact=control_name)
            except EvidenceCategory.DoesNotExist:
                # Try partial match
                controls = EvidenceCategory.objects.filter(name__icontains=control_name)
                if controls.count() == 1:
                    control = controls.first()
                else:
                    self.stdout.write(self.style.WARNING(f'Control not found: {control_name}'))
                    not_found_count += 1
                    continue
            except EvidenceCategory.MultipleObjectsReturned:
                # If multiple matches, try exact match with case
                controls = EvidenceCategory.objects.filter(name=control_name)
                if controls.exists():
                    control = controls.first()
                else:
                    self.stdout.write(self.style.WARNING(f'Multiple controls found for: {control_name}'))
                    not_found_count += 1
                    continue

            # Get assignee
            assignee = None
            if assignee_name:
                # Try to find user by first name, last name, or username
                try:
                    assignee = User.objects.get(username__iexact=assignee_name.lower().replace(' ', '_'))
                except User.DoesNotExist:
                    try:
                        assignee = User.objects.get(first_name__iexact=assignee_name)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        # Try partial match on first name
                        users = User.objects.filter(first_name__icontains=assignee_name.split()[0] if assignee_name.split() else assignee_name)
                        if users.count() == 1:
                            assignee = users.first()

            # Update control
            if assignee:
                if control.assignee != assignee:
                    control.assignee = assignee
                    control.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated: {control_name} - Assigned to {assignee.username}'))
                else:
                    self.stdout.write(f'Already assigned: {control_name} - Assigned to {assignee.username}')
            else:
                self.stdout.write(self.style.WARNING(f'Assignee "{assignee_name}" not found for: {control_name}'))
                assignee_not_found_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n[SUMMARY] Updated: {updated_count} controls, Not found: {not_found_count}, Assignee not found: {assignee_not_found_count}'
        ))
