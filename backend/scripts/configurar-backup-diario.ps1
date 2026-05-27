Param(
  [string]$TaskName = "REPOINVENT-Backup-Diario",
  [string]$ProjectDir = "C:\Users\PCHOME1\OneDrive\Documentos\REPOINVENT\backend",
  [string]$Hour = "02:00"
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $ProjectDir "scripts\backup-diario.ps1"
if (!(Test-Path -LiteralPath $scriptPath)) {
  throw "Script nao encontrado: $scriptPath"
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -ProjectDir `"$ProjectDir`""
$trigger = New-ScheduledTaskTrigger -Daily -At $Hour
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Output "Tarefa '$TaskName' configurada para rodar diariamente as $Hour."
