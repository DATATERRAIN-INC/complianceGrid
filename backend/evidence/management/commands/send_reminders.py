from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from evidence.models import EvidenceSubmission, EvidenceStatus, ReminderLog, Notification


class Command(BaseCommand):
    help = 'Send reminder emails for evidence submissions'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # 1-day reminders (1 day before due date)
        self.send_reminders(today + timedelta(days=1), '1_day')
        
        # Overdue reminders (1 day after due date)
        self.send_overdue_reminders(today)
        
        # Due date notifications (in-app notifications for assignees on due date)
        self.send_due_date_notifications(today)
        
        self.stdout.write(self.style.SUCCESS('Successfully sent reminders'))

    def send_reminders(self, due_date, reminder_type):
        submissions = EvidenceSubmission.objects.filter(
            due_date=due_date,
            status=EvidenceStatus.PENDING
        ).select_related('category', 'category__assignee', 'submitted_by')
        
        for submission in submissions:
            # Check if reminder already sent today
            if ReminderLog.objects.filter(
                submission=submission,
                reminder_type=reminder_type,
                sent_at__date=timezone.now().date()
            ).exists():
                continue
            
            # Get recipient: prioritize assignee, fallback to submitted_by
            recipient = submission.category.assignee
            if not recipient:
                recipient = submission.submitted_by
            if not recipient:
                # Try to get from category assigned reviewers
                reviewers = submission.category.assigned_reviewers.all()
                if reviewers.exists():
                    recipient = reviewers.first()
                else:
                    self.stdout.write(self.style.WARNING(f"No assignee or submitted_by for submission {submission.id}"))
                    continue
            
            self.send_email(submission, reminder_type, recipient)

    def send_overdue_reminders(self, today):
        # Only send reminders for submissions that are exactly 1 day overdue
        # (due_date + 1 day = today)
        one_day_ago = today - timedelta(days=1)
        
        submissions = EvidenceSubmission.objects.filter(
            due_date=one_day_ago,
            status=EvidenceStatus.PENDING
        ).select_related('category', 'category__assignee', 'submitted_by')
        
        for submission in submissions:
            # Check if overdue reminder already sent for this submission
            if ReminderLog.objects.filter(
                submission=submission,
                reminder_type='overdue'
            ).exists():
                continue
            
            # Get recipient: prioritize assignee, fallback to submitted_by
            recipient = submission.category.assignee
            if not recipient:
                recipient = submission.submitted_by
            if not recipient:
                reviewers = submission.category.assigned_reviewers.all()
                if reviewers.exists():
                    recipient = reviewers.first()
                else:
                    self.stdout.write(self.style.WARNING(f"No assignee or submitted_by for submission {submission.id}"))
                    continue
            
            self.send_email(submission, 'overdue', recipient)

    def send_email(self, submission, reminder_type, recipient):
        if reminder_type == 'overdue':
            subject = f"OVERDUE: Evidence Submission Required - {submission.category.name}"
            message = f"""Hello {recipient.first_name or recipient.username},

This is a reminder that your evidence submission for "{submission.category.name}" is now OVERDUE.

Due Date: {submission.due_date} (1 day ago)
Period: {submission.period_start_date} to {submission.period_end_date}

Evidence Requirements:
{submission.category.evidence_requirements}

Please submit your evidence immediately.

Best regards,
ComplianceGrid System
"""
        else:
            subject = f"Evidence Submission Reminder: {submission.category.name}"
            message = f"""Hello {recipient.first_name or recipient.username},

This is a reminder that your evidence submission for "{submission.category.name}" is due in 1 day.

Due Date: {submission.due_date}
Period: {submission.period_start_date} to {submission.period_end_date}

Evidence Requirements:
{submission.category.evidence_requirements}

Please submit your evidence as soon as possible.

Best regards,
ComplianceGrid System
"""
        
        try:
            if recipient and recipient.email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient.email],
                    fail_silently=False,
                )
                
                ReminderLog.objects.create(
                    submission=submission,
                    reminder_type=reminder_type,
                    sent_to=recipient,
                    email_sent=True
                )
                
                self.stdout.write(f"Sent {reminder_type} reminder for {submission.category.name} to {recipient.email}")
            else:
                self.stdout.write(self.style.WARNING(f"No email address for recipient {recipient.username} (submission {submission.id})"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {str(e)}"))
    
    def send_due_date_notifications(self, today):
        """Send in-app notifications to assignees on due date"""
        submissions = EvidenceSubmission.objects.filter(
            due_date=today,
            status=EvidenceStatus.PENDING
        ).select_related('category', 'category__assignee')
        
        notifications_created = 0
        for submission in submissions:
            category = submission.category
            # Send notification to assignee if exists
            if category.assignee:
                # Check if notification already exists for this submission today
                existing_notification = Notification.objects.filter(
                    user=category.assignee,
                    submission=submission,
                    notification_type='OVERDUE',
                    created_at__date=today
                ).first()
                
                if not existing_notification:
                    # Create notification with link to control-file page
                    Notification.objects.create(
                        user=category.assignee,
                        notification_type='OVERDUE',
                        title=f'Due Today: {category.name}',
                        message=f'Evidence submission for "{category.name}" is due today. Please submit your evidence files.',
                        category=category,
                        submission=submission,
                        is_read=False
                    )
                    notifications_created += 1
                    self.stdout.write(f"Created due date notification for {category.name} to {category.assignee.username}")
        
        if notifications_created > 0:
            self.stdout.write(self.style.SUCCESS(f'Created {notifications_created} due date notification(s)'))

