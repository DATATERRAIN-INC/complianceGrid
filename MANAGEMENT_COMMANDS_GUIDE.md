# Management Commands Guide

This guide lists all available Django management commands for the compliance evidence application.

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

## Full Refresh (Recommended for Setup & Reset)

### full_refresh
One command that clears submission history, removes local documents, updates users, imports/refreshes controls from CSV, and sets the default approver.

```bash
# With CSV (run from backend folder where all_categories.csv is)
python manage.py full_refresh --csv all_categories.csv
```

Or use default (looks for all_categories.csv in backend):

```bash
python manage.py full_refresh
```

**With custom CSV path:**
```bash
python manage.py full_refresh --csv path/to/all_categories.csv
```

**Preview only (no changes):**
```bash
python manage.py full_refresh --dry-run
```

**What it does:**
1. **Clear submission history** – Deletes all submissions, files, comments, reminders, and related notifications
2. **Remove local documents** – Deletes all files in `media/evidence_files/`
3. **Update users** – Syncs the predefined user list (sakthi, monisa, manoj, preeja, murugesh, vinothkumar, ajithkumar, karthikeyan, mary); removes others from assignee/approver and deletes other accounts
4. **Import/refresh controls** – Reads `all_categories.csv` (or `--csv` path) and creates or updates controls with: Control Short, Duration, To Do, Evidence, Assigned to
5. **Set default approver** – Sets Manoj as approver for all active controls that don’t have one

**When to use:**
- Initial setup
- After updating `all_categories.csv` and you want a clean reset
- When you want to wipe submission history and re-import from CSV

**CSV format:** See `IMPORT_INSTRUCTIONS.md` for column names and duration values.

---

## Category/Control Management Commands

### add_control
Add a single control manually (e.g. from Django shell or a one-off script).

**What it does:**
- Creates one control with name, group, duration, description, evidence, assignee
- Used by the standalone script in `backend/add_control.py` (configure variables and run via shell)

**When to use:**
- Adding one control without changing the CSV
- Quick tests

### assign_category_groups
Assign category groups (e.g. ACCESS_CONTROLS, NETWORK_SECURITY) to controls based on CSV.

```bash
python manage.py assign_category_groups
```

**Or with custom CSV file:**
```bash
python manage.py assign_category_groups --csv-file all_categories.csv
```

**What it does:**
- Maps control numbers from CSV to category groups
- Uses `all_categories.csv` by default (must have "No" and "Control Short" columns)

**When to use:**
- Organizing controls into compliance groups
- After a full refresh if you use category groups

---

## Submission Management Commands

### generate_submissions
Create submission records for active categories.

```bash
python manage.py generate_submissions
```

**What it does:**
- Creates submission records for all active categories
- Calculates due dates from review periods
- Only creates when no active submission exists or the current one has ended

**When to use:**
- After full refresh or when new categories are added
- Can be run daily (e.g. scheduled)

### send_reminders
Send email reminders for upcoming and overdue submissions.

```bash
python manage.py send_reminders
```

**What it does:**
- Sends emails 1 day before and 1 day after due date
- Creates in-app notifications
- Avoids duplicate emails

**When to use:**
- Daily (e.g. via Windows Task Scheduler) or for manual testing

**Setup:** See `SETUP_EMAIL_NOTIFICATIONS.md` and `SETUP_TASK_SCHEDULER.md`

---

## Maintenance Commands

### remove_duplicates
Remove duplicate categories (keeps oldest).

```bash
python manage.py remove_duplicates
```

**When to use:**
- Cleaning up duplicate category names

### remove_extra_categories
Remove categories that are not in a CSV file.

```bash
python manage.py remove_extra_categories all_categories.csv
```

**Preview only:**
```bash
python manage.py remove_extra_categories all_categories.csv --dry-run
```

**What it does:**
- Compares database categories with CSV ("Control Short" column)
- Deletes categories not listed in the CSV

**When to use:**
- Syncing database with CSV after removing rows from the CSV

---

## Typical Workflows

### Initial Setup (First Time)

```bash
cd backend
venv\Scripts\activate   # Windows (or source venv/bin/activate on Linux/Mac)

# 1. Full refresh: users, controls from CSV, default approver (run from backend)
python manage.py full_refresh --csv all_categories.csv

# 2. Optional: assign category groups if you use them
python manage.py assign_category_groups

# 3. Generate initial submissions
python manage.py generate_submissions
```

### Regular Maintenance

```bash
# Daily (can be automated):
python manage.py generate_submissions
python manage.py send_reminders
```

### After Updating all_categories.csv (Full Reset)

```bash
# Reset everything and re-import from CSV (run from backend)
python manage.py full_refresh --csv all_categories.csv

# Optional: reassign category groups, then submissions
python manage.py assign_category_groups
python manage.py generate_submissions
```

---

## Command Reference Quick List

| Command | Purpose | Frequency |
|---------|---------|-----------|
| `full_refresh` | Clear history, update users, import/refresh from CSV, set approver | Setup / after CSV changes |
| `add_control` | Add single control | As needed |
| `assign_category_groups` | Assign groups to controls | After full refresh if needed |
| `generate_submissions` | Create submission records | Daily or after refresh |
| `send_reminders` | Send email reminders | Daily (automated) |
| `remove_duplicates` | Remove duplicate categories | As needed |
| `remove_extra_categories` | Remove categories not in CSV | As needed |

---

## Troubleshooting

### Command not found?
- Run commands from the `backend` directory
- Activate the virtual environment
- Check Django: `pip list | grep Django`

### CSV / full_refresh issues?
- Default CSV path is `backend/all_categories.csv`; use `--csv` for another path
- See `IMPORT_INSTRUCTIONS.md` for CSV format and column names
- Use `python manage.py full_refresh --dry-run` to see what would be done

### Email not sending?
- See `SETUP_EMAIL_NOTIFICATIONS.md`
- Test: `python manage.py send_reminders`
- Ensure assignees have email addresses

---

## Additional Resources

- **Import instructions & CSV format:** `IMPORT_INSTRUCTIONS.md`
- **Email setup:** `SETUP_EMAIL_NOTIFICATIONS.md`
- **Task Scheduler:** `SETUP_TASK_SCHEDULER.md`
- **Google OAuth:** `SETUP_GOOGLE_OAUTH.md`
