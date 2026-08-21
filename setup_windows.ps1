# Installs a weekly Windows Scheduled Task (every Monday 09:00) that runs check_versions.py.
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $dir "check_versions.py"
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = (Get-Command py -ErrorAction SilentlyContinue).Source }
if (-not $python) { Write-Error "Python niet gevonden. Installeer Python 3 via python.org en probeer opnieuw."; exit 1 }

$action = New-ScheduledTaskAction -Execute $python -Argument "`"$script`"" -WorkingDirectory $dir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "SoftwareVersionChecker" -Action $action -Trigger $trigger -Force

Write-Host "Geinstalleerd: draait elke maandag 09:00."
Write-Host "Uitschakelen met: Unregister-ScheduledTask -TaskName SoftwareVersionChecker"
