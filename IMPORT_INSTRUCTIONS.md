# How to Import Categories from CSV

## Step 1: Prepare Your CSV File

Your CSV file should have these columns (column names can vary):

**Required columns:**
- `Control Short` or `Control` or `Name` or `Category` - The category name
- `Duration` or `Review Period` or `Period` - The review frequency

**Optional columns:**
- `To Do` or `Description` or `Requirements` - Category description
- `Evidence` or `Evidence Requirements` - What evidence is needed
- `Assigned to` or `Assigned` - Who is responsible

### Example CSV Format:

```csv
Control Short,Duration,To Do,Evidence,Assigned to
Code of Conduct,Annually,Update all the policy into keka and get acknowledgement,Employee handbook and acknowledged employee handbook,Preeja
Signed NDA,Monthly,Non-Disclosure Agreement management,Employee handbook and acknowledged employee handbook,HR
ISMS Policy,Annually,Information Security Management System policy,Policy documentation and acknowledgements,Monisa
```

### Duration values (only these 6 are supported; case-insensitive):
- `Daily`
- `Weekly`
- `Monthly`
- `Quarterly`
- `Half yearly` (or `Half Yearly`)
- `Annually`

**Note:** Any other value in the CSV is stored as null (no duration set).

## Step 2: Save Your CSV File

1. Export your control matrix from Excel/Google Sheets to CSV format
2. Save the file with a name like `all_categories.csv`
3. Place it in the `backend` folder of the project:
   ```
   complianceGrid/
   └── backend/
       └── all_categories.csv  ← Put your file here
   ```

## Step 3: Run Full Refresh (Import + Reset)

The **full_refresh** command does everything in one go: clears submission history, removes local documents, updates users, imports/refreshes controls from your CSV, and sets the default approver.

Open a terminal/PowerShell in the `backend` folder and run:

```bash
# Activate virtual environment (if not already activated)
.\venv\Scripts\Activate.ps1

# Run full refresh with the CSV (from backend folder)
python manage.py full_refresh --csv all_categories.csv
```

Or use the default (looks for `all_categories.csv` in the backend directory):

```bash
python manage.py full_refresh
```

With a custom CSV path:

```bash
python manage.py full_refresh --csv path/to/all_categories.csv
```

To preview changes without applying them:

```bash
python manage.py full_refresh --dry-run
```

**What full_refresh does:**
1. Clears all submission history (submissions, files, comments, notifications)
2. Removes local document files from `media/evidence_files/`
3. Updates/syncs users (same set as before: sakthi, monisa, manoj, preeja, etc.)
4. Imports or updates all controls from the CSV (Control Short, Duration, To Do, Evidence, Assigned to)
5. Sets Manoj as default approver for controls that don’t have one

## Step 4: Optional – Generate Submissions

After a full refresh, you can create submission records for the current period:

```bash
python manage.py generate_submissions
```

## Step 5: Verify the Import

Check how many categories exist:

```bash
python manage.py shell -c "from evidence.models import EvidenceCategory; print(f'Total categories: {EvidenceCategory.objects.count()}')"
```

## Troubleshooting

### If you get "CSV file not found":
- By default, the script looks for `all_categories.csv` in the `backend` folder
- Use `--csv` to specify a path: `python manage.py full_refresh --csv "C:\full\path\to\file.csv"`

### If column names don't match:
The command supports these column name variations:
- Name: `Control Short`, `Control`, `Name`, `Category`
- Duration: `Duration`, `Review Period`, `Period`
- Description: `To Do`, `Description`, `Requirements`
- Evidence: `Evidence`, `Evidence Requirements`
- Assigned: `Assigned to`, `Assigned`

### If you see encoding errors:
- Save your CSV as UTF-8 (e.g. in Excel: Save As → CSV UTF-8 (Comma delimited) (*.csv))

## Example: Full Import Process

1. **Export from Excel:**
   - Open your control matrix in Excel
   - File → Save As
   - Choose "CSV UTF-8 (Comma delimited) (*.csv)"
   - Save as `all_categories.csv` in the `backend` folder

2. **Full refresh (reset + import):**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python manage.py full_refresh --csv all_categories.csv
   ```

3. **Generate submissions (optional):**
   ```bash
   python manage.py generate_submissions
   ```

That’s it. Your categories are imported and ready to use.
