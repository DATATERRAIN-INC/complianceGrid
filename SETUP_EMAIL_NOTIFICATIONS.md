# Setting Up Email Notifications with Gmail

This guide explains how to configure email notifications to send reminders to assignees one day before the due date.

## Step 1: Enable 2-Step Verification (Required First)

**Important:** App passwords are only available after enabling 2-Step Verification. If you don't see "App passwords", you need to enable 2-Step Verification first.

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **Security & sign-in** (or just **Security**)
3. Find **2-Step Verification** section
4. If it says "2-Step Verification is off", click on it to enable
5. Follow the setup wizard:
   - Choose your verification method (phone number, authenticator app, etc.)
   - Complete the verification process
   - Click **Turn On** to enable 2-Step Verification

## Step 2: Create a Gmail App Password

Once 2-Step Verification is enabled:

1. Go back to **Security** → **2-Step Verification**
2. Scroll down to find **App passwords** (this option will now be visible)
3. Click on **App passwords**
4. You may need to sign in again
5. Click **Select app** → Choose "Mail"
6. Click **Select device** → Choose "Other (Custom name)" → Enter "ComplianceGrid"
7. Click **Generate**
8. **Copy the 16-character password** (you'll need this for the .env file)
   - The password will look like: `abcd efgh ijkl mnop` (16 characters with spaces, but use without spaces)

## Step 3: Update .env File

Edit `backend/.env` and add your Gmail credentials:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:** Use the **App Password** (16 characters), not your regular Gmail password.

## Step 4: Test Email Configuration

Run the Django shell to test:

```bash
cd backend
python manage.py shell
```

Then in the shell:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from ComplianceGrid',
    settings.DEFAULT_FROM_EMAIL,
    ['your-test-email@gmail.com'],
    fail_silently=False,
)
```

If successful, you should receive the test email.

## Step 5: Run Reminders Manually

To send reminders immediately (for testing):

```bash
cd backend
python manage.py send_reminders
```

This command will:
- **Send emails 1 day before due date**
- **Send emails 1 day after due date if overdue**
- Create in-app notifications for items due today

## Step 6: Schedule Automatic Reminders

### Option A: Windows Task Scheduler (Recommended for Windows)

1. Open **Task Scheduler** (search in Windows)
2. Click **Create Basic Task**
3. Name: "ComplianceGrid Daily Reminders"
4. Trigger: **Daily** at your preferred time (e.g., 9:00 AM)
5. Action: **Start a program**
6. Program: `python`
7. Arguments: `manage.py send_reminders`
8. Start in: `C:\Users\monisa.DATATERRAINAD\complianceGrid\backend`
9. Check **Run whether user is logged on or not**
10. Click **Finish**

### Option B: PowerShell Scheduled Task

Run PowerShell as Administrator:

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "manage.py send_reminders" -WorkingDirectory "C:\Users\monisa.DATATERRAINAD\complianceGrid\backend"
$trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
Register-ScheduledTask -TaskName "ComplianceGrid Reminders" -Action $action -Trigger $trigger
```

### Option C: Cron Job (Linux/Mac)

Add to crontab:

```bash
# Send reminders daily at 9 AM
0 9 * * * cd /path/to/complianceGrid/backend && python manage.py send_reminders
```

## How It Works

The `send_reminders` command:
1. Finds all submissions with due dates matching:
   - **Today + 1 day** (1-day before due date reminders)
   - **Today - 1 day** (1-day after due date - overdue reminders)
2. Sends emails to the **assignee** of each control
3. Logs all sent reminders to prevent duplicates
4. Only sends one reminder per submission (prevents duplicate emails)

## Troubleshooting

### Can't see "App passwords" option?
- **You must enable 2-Step Verification first** - App passwords only appear after 2-Step Verification is enabled
- Go to Security → 2-Step Verification → Turn it on
- After enabling, refresh the page and "App passwords" will appear below the 2-Step Verification section

### Email not sending?
- Verify App Password is correct (16 characters, remove spaces if copied with spaces)
- Check `EMAIL_HOST_USER` matches your Gmail address exactly
- Ensure 2-Step Verification is enabled (required for App passwords)
- Check Django logs for error messages
- Try generating a new App Password if the current one doesn't work

### Emails going to spam?
- Add `noreply@compliancegrid.com` to your contacts
- Check spam folder
- Consider using a custom domain email for production

### No emails received?
- Verify assignees have email addresses in their user profiles
- Check that controls have assignees set
- Run the command manually to see error messages
