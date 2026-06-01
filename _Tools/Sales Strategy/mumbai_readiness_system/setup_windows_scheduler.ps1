param(
  [string]$PythonPath = 'python'
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pipeline = Join-Path $root 'run_pipeline.py'

$dailyAction = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$pipeline`""
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName 'DigiVenue_Daily_Readiness_Pipeline' -Action $dailyAction -Trigger $dailyTrigger -Description 'Daily Mumbai readiness intelligence pipeline' -Force

$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM
Register-ScheduledTask -TaskName 'DigiVenue_Weekly_Strategy_Report' -Action $dailyAction -Trigger $weeklyTrigger -Description 'Weekly refresh and strategy report' -Force

Write-Host 'Scheduled tasks created/updated.'
