# Management Commands Guide

This guide lists all available Django management commands for updating users, categories, and managing the application.

## Prerequisites

1. **Activate Virtual Environment:**
   ```bash
   cd backend
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. **Ensure you're in the backend directory:**
   ```bash
   cd backend
   ```

---

## User Management Commands

### 1. Update Users
Updates user profiles and removes other users from assignee/approver fields.

```bash
python manage.py update_users
```

**What it does:**
- Updates or creates predefined users (sakthi, monisa, manoj, preeja, etc.)
- Sets default password: `Data@123`
- Removes other users from assignee/approver fields
- Deletes other user accounts

**When to use:**
- Initial setup
- When you need to reset user passwords
- When cleaning up old user accounts

---

## Category/Control Management Commands

### 2. Import Controls from CSV
Import categories/controls from a CSV file.

```bash
python manage.py import_controls_csv all_categories.csv --create-users
```

**What it does:**
- Creates/updates categories from CSV file
- Sets review periods (Daily, Weekly, Monthly, Quarterly, Half Yearly, Annually)
- Assigns assignees to categories
- Sets Manoj as default approver
- Optionally creates user accounts if `--create-users` flag is used

**When to use:**
- Initial import of controls
- Bulk update of controls from CSV
- Adding new controls

**CSV Format:** See `IMPORT_INSTRUCTIONS.md` for details

### 3. Add a Single Control
Add one control manually.

```bash
python manage.py add_control --name "Control Name" --group "SECURITY" --duration "Monthly" --description "Description" --evidence "Evidence requirements" --assignee "username"
```

**What it does:**
- Creates a single control with all specified fields
- Sets Manoj as default approver

**When to use:**
- Adding a single control quickly
- Testing control creation

### 4. Update Assignees
Update assignees for specific controls.

```bash
python manage.py update_assignees
```

**What it does:**
- Updates assignees for a hardcoded list of controls
- Matches controls by name (flexible matching)

**When to use:**
- Bulk updating assignees for specific controls
- Reassigning controls to different users

### 5. Update Controls from CSV
Update both assignee and duration for controls.

```bash
python manage.py update_controls_from_csv
```

**What it does:**
- Updates assignee and review period for a hardcoded list of controls
- Matches controls by name (flexible matching)

**When to use:**
- Bulk updating both assignee and duration
- When you have a list of controls to update

### 6. Set Default Approver
Set Manoj as the default approver for all controls without an approver.

```bash
python manage.py set_default_approver
```

**Options:**
- `--force`: Update all controls, even if they already have an approver

```bash
python manage.py set_default_approver --force
```

**What it does:**
- Sets Manoj as approver for controls without an approver
- With `--force`, updates all controls

**When to use:**
- After importing controls
- When you need to ensure all controls have an approver

### 7. Assign Category Groups
Assign category groups to controls based on CSV.

```bash
python manage.py assign_category_groups
```

**Or with custom CSV file:**
```bash
python manage.py assign_category_groups --csv-file all_categories.csv
```

**What it does:**
- Assigns category groups (ACCESS_CONTROLS, NETWORK_SECURITY, DATA_PROTECTION, etc.) to controls
- Uses `all_categories.csv` by default (must have "No" and "Control Short" columns)
- Maps control numbers to predefined category groups

**When to use:**
- Organizing controls into compliance groups
- After importing controls

### 8. Assign Users to Categories
Assign users to categories from CSV.

```bash
python manage.py assign_users_to_categories all_categories.csv
```

**Or with user creation:**
```bash
python manage.py assign_users_to_categories all_categories.csv --create-users
```

**What it does:**
- Assigns users to categories based on CSV file
- CSV should have "Control Short" and "Assigned to" columns
- Uses `all_categories.csv` (which contains these columns)
- Optionally creates user accounts if `--create-users` flag is used

**When to use:**
- Bulk assigning users to controls
- Reassigning controls to different users
- After importing controls to set assignees

---

## Submission Management Commands

### 9. Generate Submissions
Automatically generate submission records for active categories.

```bash
python manage.py generate_submissions
```

**What it does:**
- Creates submission records for all active categories
- Calculates due dates based on review periods
- Only creates if no active submission exists or current one has ended

**When to use:**
- Initial setup
- Daily/weekly (can be scheduled)
- After creating new categories

### 10. Send Reminders
Send email reminders for upcoming and overdue submissions.

```bash
python manage.py send_reminders
```

**What it does:**
- Sends emails 1 day before due date
- Sends emails 1 day after due date (if overdue)
- Creates in-app notifications
- Prevents duplicate emails

**When to use:**
- Daily (should be scheduled via Windows Task Scheduler)
- Manual testing

**Setup:** See `SETUP_EMAIL_NOTIFICATIONS.md` and `SETUP_TASK_SCHEDULER.md`

---

## Maintenance Commands

### 11. Remove Local Documents
Remove all local document files from the media directory.

```bash
python manage.py remove_local_documents
```

**Options:**
- `--dry-run`: Show what would be deleted without actually deleting
- `--keep-records`: Keep database records but remove file references

```bash
python manage.py remove_local_documents --dry-run
python manage.py remove_local_documents --keep-records
```

**What it does:**
- Deletes all files from `backend/media/evidence_files/`
- Optionally clears file references from database

**When to use:**
- Cleaning up local storage
- Before migrating to cloud-only storage
- Freeing up disk space

### 12. Remove Duplicates
Remove duplicate categories, keeping the oldest one.

```bash
python manage.py remove_duplicates
```

**What it does:**
- Finds categories with duplicate names
- Keeps the oldest one
- Deletes duplicates

**When to use:**
- After importing data multiple times
- Cleaning up duplicate entries

### 13. Remove Extra Categories
Remove categories that are not in a CSV file.

```bash
python manage.py remove_extra_categories all_categories.csv
```

**Or with dry run (preview only):**
```bash
python manage.py remove_extra_categories all_categories.csv --dry-run
```

**What it does:**
- Compares database categories with CSV file
- Removes categories not in CSV (based on "Control Short" column)
- Keeps only categories listed in CSV
- Use `--dry-run` to preview what would be deleted

**When to use:**
- Cleaning up unwanted categories
- After major CSV updates
- Syncing database with CSV file

---

## Typical Setup Workflow

### Initial Setup (First Time)

```bash
# 1. Activate virtual environment
cd backend
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# 2. Update/create users
python manage.py update_users

# 3. Import controls from CSV
python manage.py import_controls_csv all_categories.csv --create-users

# 4. Set default approver (if needed)
python manage.py set_default_approver

# 5. Generate initial submissions
python manage.py generate_submissions

# 6. Test email reminders
python manage.py send_reminders
```

### Regular Maintenance

```bash
# Daily (should be automated):
python manage.py generate_submissions  # Create new submissions
python manage.py send_reminders        # Send email reminders

# As needed:
python manage.py update_users          # Update user accounts
python manage.py set_default_approver  # Ensure all have approvers
```

### Bulk Updates

```bash
# Update controls from CSV (use all_categories.csv)
python manage.py import_controls_csv all_categories.csv --create-users

# Assign users to categories from CSV
python manage.py assign_users_to_categories all_categories.csv

# Assign category groups
python manage.py assign_category_groups

# Update specific assignees (hardcoded list)
python manage.py update_assignees

# Update assignees and durations (hardcoded list)
python manage.py update_controls_from_csv
```

---

## Command Reference Quick List

| Command | Purpose | Frequency |
|---------|---------|-----------|
| `update_users` | Update/create users | As needed |
| `import_controls_csv` | Import/update controls | When CSV changes |
| `add_control` | Add single control | As needed |
| `update_assignees` | Update assignees | As needed |
| `update_controls_from_csv` | Update assignees & durations | As needed |
| `set_default_approver` | Set Manoj as approver | After imports |
| `assign_category_groups` | Assign groups | After imports |
| `assign_users_to_categories` | Bulk assign users | As needed |
| `generate_submissions` | Create submissions | Daily (automated) |
| `send_reminders` | Send email reminders | Daily (automated) |
| `remove_local_documents` | Clean up files | As needed |
| `remove_duplicates` | Clean duplicates | As needed |
| `remove_extra_categories` | Remove unwanted | As needed |

---

## Troubleshooting

### Command not found?
- Make sure you're in the `backend` directory
- Ensure virtual environment is activated
- Check that Django is installed: `pip list | grep Django`

### Permission errors?
- Make sure you have write permissions
- Check database connection
- Verify `.env` file is configured

### Import errors?
- Check CSV file format (see `IMPORT_INSTRUCTIONS.md`)
- Verify CSV file path is correct (default is `all_categories.csv` in backend directory)
- Check that required columns exist ("Control Short", "Duration", "Assigned to", etc.)
- Ensure CSV file is saved in the `backend` directory

### Email not sending?
- Verify email configuration in `.env` (see `SETUP_EMAIL_NOTIFICATIONS.md`)
- Test with: `python manage.py send_reminders`
- Check that assignees have email addresses

---

## Additional Resources

- **Import Instructions:** `IMPORT_INSTRUCTIONS.md`
- **Email Setup:** `SETUP_EMAIL_NOTIFICATIONS.md`
- **Task Scheduler:** `SETUP_TASK_SCHEDULER.md`
- **Google OAuth:** `SETUP_GOOGLE_OAUTH.md`
