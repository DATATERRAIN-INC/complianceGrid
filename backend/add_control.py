"""
Quick script to add a control under Security category group.
Run this with: python manage.py shell < add_control.py
Or run: python manage.py shell
Then copy-paste the code below.
"""

from evidence.models import EvidenceCategory, ReviewPeriod, CategoryGroup
from django.contrib.auth.models import User

# ===== CONFIGURE YOUR CONTROL HERE =====
CONTROL_NAME = "Your Control Name Here"
SECURITY_GROUP = "NETWORK_SECURITY"  # Options: ACCESS_CONTROLS, NETWORK_SECURITY, PHYSICAL_SECURITY, DATA_PROTECTION, ENDPOINT_SECURITY, MONITORING_INCIDENT
DURATION = "Monthly"  # Options: Daily, Weekly, Monthly, Quarterly, Half Yearly, Annually
DESCRIPTION = "Control description here"
EVIDENCE_REQUIREMENTS = "Evidence requirements here"
ASSIGNED_TO_USERNAME = None  # e.g., "monisa" or None

# Only these 6 duration options are supported. Any other value → review_period = None.
duration_map = {
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

# Get review period (None if invalid)
review_period = duration_map.get(DURATION) or duration_map.get((DURATION or '').strip().lower()) if DURATION else None

# Get category group
category_group = getattr(CategoryGroup, SECURITY_GROUP, CategoryGroup.UNCATEGORIZED)

# Get assignee if provided
assignee = None
if ASSIGNED_TO_USERNAME:
    try:
        assignee = User.objects.get(username=ASSIGNED_TO_USERNAME)
    except User.DoesNotExist:
        print(f"Warning: User '{ASSIGNED_TO_USERNAME}' not found. Creating control without assignee.")

# Create the control (review_period can be None for invalid duration)
defaults = {
    'description': DESCRIPTION,
    'evidence_requirements': EVIDENCE_REQUIREMENTS,
    'category_group': category_group,
    'is_active': True,
    'assignee': assignee,
}
if review_period is not None:
    defaults['review_period'] = review_period
category, created = EvidenceCategory.objects.get_or_create(name=CONTROL_NAME, defaults=defaults)

if created:
    print(f"✓ Successfully created control: {CONTROL_NAME}")
    print(f"  - Group: {category_group.label}")
    print(f"  - Duration: {review_period.label if review_period else '(not set)'}")
    if assignee:
        print(f"  - Assigned to: {assignee.username}")
else:
    print(f"⚠ Control '{CONTROL_NAME}' already exists. Updating...")
    category.description = DESCRIPTION
    category.evidence_requirements = EVIDENCE_REQUIREMENTS
    category.review_period = review_period
    category.category_group = category_group
    if assignee:
        category.assignee = assignee
    category.save()
    print(f"✓ Successfully updated control: {CONTROL_NAME}")
