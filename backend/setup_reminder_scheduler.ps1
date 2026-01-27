# ComplianceGrid - Setup Email Reminder Scheduler
# This script sets up a Windows Scheduled Task to run send_reminders daily

Write-Host "=== ComplianceGrid Email Reminder Scheduler Setup ===" -ForegroundColor Cyan

# Get the backend directory path
$backendPath = $PSScriptRoot
if (-not (Test-Path "$backendPath\manage.py")) {
    Write-Host "ERROR: manage.py not found in $backendPath" -ForegroundColor Red
    Write-Host "Please run this script from the backend directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "Backend directory: $backendPath" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`nWARNING: This script requires Administrator privileges." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host "`nRight-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Get Python executable path
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and added to PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host "Python found: $pythonPath" -ForegroundColor Green

# Task configuration
$taskName = "ComplianceGrid Daily Reminders"
$taskDescription = "Sends email reminders to assignees 1 day before and 1 day after due dates"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "`nTask '$taskName' already exists." -ForegroundColor Yellow
    $response = Read-Host "Do you want to update it? (Y/N)"
    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task." -ForegroundColor Green
}

# Get schedule time from user
Write-Host "`nWhen should reminders be sent daily?" -ForegroundColor Cyan
Write-Host "Enter time in 24-hour format (e.g., 09:00 for 9 AM, 14:30 for 2:30 PM)" -ForegroundColor Gray
$timeInput = Read-Host "Time (default: 09:00)"

if ([string]::IsNullOrWhiteSpace($timeInput)) {
    $timeInput = "09:00"
}

# Validate time format
try {
    $time = [DateTime]::ParseExact($timeInput, "HH:mm", $null)
    $timeString = $time.ToString("HH:mm")
} catch {
    Write-Host "ERROR: Invalid time format. Please use HH:mm format (e.g., 09:00)" -ForegroundColor Red
    exit 1
}

Write-Host "`nCreating scheduled task..." -ForegroundColor Cyan

# Create the action (what to run)
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "manage.py send_reminders" -WorkingDirectory $backendPath

# Create the trigger (when to run - daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $timeString

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create the principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription -Force | Out-Null
    
    Write-Host "`n[SUCCESS] Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "`nTask Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at $timeString" -ForegroundColor White
    Write-Host "  Command: $pythonPath manage.py send_reminders" -ForegroundColor White
    Write-Host "  Working Directory: $backendPath" -ForegroundColor White
    
    Write-Host "`nTo verify the task:" -ForegroundColor Yellow
    Write-Host "  1. Open Task Scheduler" -ForegroundColor Gray
    Write-Host "  2. Look for '$taskName' in the task list" -ForegroundColor Gray
    
    Write-Host "`nTo test the task manually:" -ForegroundColor Yellow
    Write-Host "  cd $backendPath" -ForegroundColor Gray
    Write-Host "  python manage.py send_reminders" -ForegroundColor Gray
    
    Write-Host "`nTo run the task now:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    
} catch {
    Write-Host "`n[ERROR] Failed to create scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
