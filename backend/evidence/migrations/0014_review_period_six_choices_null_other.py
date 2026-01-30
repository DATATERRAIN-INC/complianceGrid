# Generated manually: restrict duration to 6 options; set other values to null

from django.db import migrations, models

ALLOWED_REVIEW_PERIODS = [
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'QUARTERLY',
    'HALF_YEARLY_QUARTERLY',
    'ANNUALLY',
]


def set_invalid_review_periods_to_null(apps, schema_editor):
    EvidenceCategory = apps.get_model('evidence', 'EvidenceCategory')
    EvidenceCategory.objects.exclude(
        review_period__in=ALLOWED_REVIEW_PERIODS
    ).update(review_period=None)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('evidence', '0013_add_user_google_drive_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evidencecategory',
            name='review_period',
            field=models.CharField(
                blank=True,
                choices=[
                    ('DAILY', 'Daily'),
                    ('WEEKLY', 'Weekly'),
                    ('MONTHLY', 'Monthly'),
                    ('QUARTERLY', 'Quarterly'),
                    ('HALF_YEARLY_QUARTERLY', 'Half yearly'),
                    ('ANNUALLY', 'Annually'),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.RunPython(set_invalid_review_periods_to_null, noop),
    ]
