from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from evidence.models import EvidenceCategory, ReviewPeriod


class Command(BaseCommand):
    help = 'Update assignee and duration for controls from provided CSV data'

    def handle(self, *args, **options):
        # CSV data provided by user
        controls_data = [
            {'name': 'Policy Management', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Signed NDA', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Acceptable Use policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'MRM_CISO Meetings', 'duration': 'Quarterly', 'assignee': 'Monisa'},
            {'name': 'Business meetings', 'duration': 'weekly', 'assignee': 'Preeja'},
            {'name': 'Organisation Charts', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'ISMS Policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Key roles and responsibilities', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'HR Policies', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'JD in place', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Offer letter & Appointment letter', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Manpower planning', 'duration': 'Monthly', 'assignee': 'Monisa'},
            {'name': 'External BGV', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'New Hire Functional Training', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'ISMS Training', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Refresher Training on ISMS', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Roles and Responsibilities', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Performance Appraisals', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'System Access Review', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Client Contracts with Confidentiality Clause', 'duration': 'Monthly', 'assignee': 'Manoj'},
            {'name': 'Complaints', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Changes to system boundaries', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Reporting of incidents to external users', 'duration': 'Monthly', 'assignee': 'Manoj'},
            {'name': 'Risk Assessment', 'duration': 'Annually', 'assignee': 'Karthikeyan'},
            {'name': 'Patch Management', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'Review of incidents in committee meetings', 'duration': 'Monthly', 'assignee': 'Karthikeyan'},
            {'name': 'Firewall logs', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Closure of VAPT Gaps', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Access Management policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Access Management Least Privileges', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Creating client user accounts on cloud application', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'Cloud Infra MFA', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'Asset Register', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Account sharing prohibited', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'VPN, TLS or other transit encryption.', 'duration': 'Annually', 'assignee': 'Ajith'},
            {'name': 'Whitelisted IPs', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Classification of Data', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Cloud admin access', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'VPN for cloud server', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'Email from HR to IT for Joiners and Leavers', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Privileged access approvals', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Privileged Access Reviews', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Exit Formalities', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Visitor Register', 'duration': 'Quarterly', 'assignee': 'Mary'},
            {'name': 'Physical Access Setup by HR', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Sensitive Areas Physical Access Review periodically', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Revocation of Physical Access', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Return ID cards', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Physical Access Reconciliation', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Media handling policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Firewall installation', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Application logs', 'duration': 'Monthly', 'assignee': 'Vinoth'},
            {'name': 'Active Directory', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Data Encryption', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'Encryption policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Encrypted VPN connections', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Backup Media Encryption', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'Cloud DB encryption', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'Antivirus Installed', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Regular Update of AV Definitions', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Local admin access', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Reporting of virus detected', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Internal Vulnerability Scans', 'duration': 'Monthly', 'assignee': 'Karthikeyan'},
            {'name': 'Configuration Changes are approved', 'duration': 'Annually', 'assignee': 'Monisa'},
            {'name': 'Alerts from firewall for suspicious activity', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'IT Help desk support', 'duration': 'Monthly', 'assignee': 'Ajith'},
            {'name': 'Incident Tracker', 'duration': 'Monthly', 'assignee': 'Preeja'},
            {'name': 'Change management policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'SDLC policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Change request tracker', 'duration': 'Monthly', 'assignee': 'Monisa'},
            {'name': 'Development Peer review', 'duration': 'Monthly', 'assignee': 'Monisa'},
            {'name': 'Static code analysis', 'duration': 'Monthly', 'assignee': 'Karthikeyan'},
            {'name': 'Regression Testing', 'duration': 'Quarterly', 'assignee': 'Monisa'},
            {'name': 'Release plan / UAT testing', 'duration': 'Annually', 'assignee': 'Monisa'},
            {'name': 'Segregation of Roles in change management', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'BCP Plan and documentation', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Cloud Infra processing capacity - CloudWatch', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'Environmental Controls', 'duration': 'Quarterly', 'assignee': 'Mary'},
            {'name': 'Environmental Maintenance', 'duration': 'Annually', 'assignee': 'Mary'},
            {'name': 'Backup policy', 'duration': 'Annually', 'assignee': 'Preeja'},
            {'name': 'Automated backup scripts', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'Alerts for failed backup', 'duration': 'Monthly', 'assignee': 'Murugesh'},
            {'name': 'BCP Testing', 'duration': 'Annually', 'assignee': 'Murugesh'},
            {'name': 'Retention policy', 'duration': 'Annually', 'assignee': 'Preeja'},
        ]

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

        updated_count = 0
        not_found_count = 0
        assignee_not_found_count = 0

        for control_data in controls_data:
            control_name = control_data['name']
            duration_str = control_data['duration']
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

            # Get review period
            review_period = duration_map.get(duration_str) or duration_map.get(duration_str.lower()) or ReviewPeriod.MONTHLY

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
            updated = False
            if control.review_period != review_period:
                control.review_period = review_period
                updated = True

            if assignee and control.assignee != assignee:
                control.assignee = assignee
                updated = True
            elif not assignee:
                self.stdout.write(self.style.WARNING(f'Assignee "{assignee_name}" not found for: {control_name}'))
                assignee_not_found_count += 1

            if updated:
                control.save()
                updated_count += 1
                assignee_info = f' (Assigned to {assignee.username})' if assignee else ''
                self.stdout.write(self.style.SUCCESS(f'Updated: {control_name} - {review_period.label}{assignee_info}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n[SUMMARY] Updated: {updated_count} controls, Not found: {not_found_count}, Assignee not found: {assignee_not_found_count}'
        ))
