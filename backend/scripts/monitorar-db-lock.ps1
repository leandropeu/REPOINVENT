Param(
  [string]$ProjectDir = "C:\Users\PCHOME1\OneDrive\Documentos\REPOINVENT\backend",
  [int]$Minutes = 60
)

$ErrorActionPreference = "Stop"
$logPath = Join-Path $ProjectDir "logs\security.log"

if (!(Test-Path -LiteralPath $logPath)) {
  Write-Output "Sem log de seguranca ainda: $logPath"
  exit 0
}

$start = (Get-Date).AddMinutes(-1 * $Minutes)
$pattern = "sqlite_locked"
$hits = 0

Get-Content -LiteralPath $logPath | ForEach-Object {
  if ($_ -match $pattern) {
    $dateText = $_.Split(" ")[0]
    try {
      $lineDate = [datetime]::Parse($dateText)
      if ($lineDate -ge $start) { $hits++ }
    } catch {
      $hits++
    }
  }
}

if ($hits -gt 0) {
  Write-Output "ALERTA: encontrados $hits eventos sqlite_locked nos ultimos $Minutes minutos."
  exit 1
}

Write-Output "OK: nenhum evento sqlite_locked nos ultimos $Minutes minutos."
