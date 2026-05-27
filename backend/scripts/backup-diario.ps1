Param(
  [string]$ProjectDir = "C:\Users\PCHOME1\OneDrive\Documentos\REPOINVENT\backend",
  [string]$PythonExe = ".\.venv\Scripts\python.exe",
  [int]$KeepDays = 30
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $ProjectDir

& $PythonExe -m app.run_backup --backup-dir "backups" --keep-days $KeepDays
