Param(
  [string]$ProjectDir = "C:\Users\PCHOME1\OneDrive\Documentos\REPOINVENT\backend",
  [int]$LookbackDays = 30
)

$ErrorActionPreference = "Stop"

function Add-Result {
  Param(
    [string]$Item,
    [string]$Status,
    [string]$Details
  )
  $script:results += [pscustomobject]@{
    Item = $Item
    Status = $Status
    Details = $Details
  }
}

$results = @()
$now = Get-Date
$rootDir = Split-Path -Parent $ProjectDir
$securityLog = Join-Path $ProjectDir "logs\security.log"
$backupDir = Join-Path $ProjectDir "backups"

try {
  if (Test-Path -LiteralPath $backupDir) {
    $recentBackup = Get-ChildItem -LiteralPath $backupDir -File -ErrorAction SilentlyContinue |
      Sort-Object LastWriteTime -Descending |
      Select-Object -First 1
    if ($null -ne $recentBackup) {
      Add-Result "Backups" "OK" ("Ultimo backup: {0} ({1})" -f $recentBackup.Name, $recentBackup.LastWriteTime)
    } else {
      Add-Result "Backups" "ALERTA" "Pasta de backups existe, mas sem arquivos."
    }
  } else {
    Add-Result "Backups" "ALERTA" "Pasta de backups nao encontrada."
  }
} catch {
  Add-Result "Backups" "ERRO" $_.Exception.Message
}

foreach ($taskName in @("REPOINVENT-Backup-Diario", "REPOINVENT-Monitor-DB-Lock")) {
  try {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
    Add-Result "Task $taskName" "OK" ("Estado: {0}" -f $task.State)
  } catch {
    Add-Result "Task $taskName" "ALERTA" "Tarefa nao encontrada."
  }
}

try {
  if (Test-Path -LiteralPath $securityLog) {
    $lines = Get-Content -LiteralPath $securityLog -ErrorAction Stop
    $patterns = @("sqlite_locked", "security_event status=401", "security_event status=403", "security_event status=429", "security_event status=5")
    foreach ($pattern in $patterns) {
      $count = ($lines | Where-Object { $_ -like "*$pattern*" }).Count
      Add-Result "Log pattern $pattern" "OK" ("Ocorrencias: $count")
    }
  } else {
    Add-Result "Logs" "ALERTA" "Arquivo security.log nao encontrado."
  }
} catch {
  Add-Result "Logs" "ERRO" $_.Exception.Message
}

try {
  $envPath = Join-Path $ProjectDir ".env"
  if (Test-Path -LiteralPath $envPath) {
    $envLines = Get-Content -LiteralPath $envPath
    $secretLine = $envLines | Where-Object { $_ -match "^SECRET_KEY=" } | Select-Object -First 1
    if ($secretLine) {
      $secret = $secretLine.Substring("SECRET_KEY=".Length)
      if ($secret.Length -ge 32) {
        Add-Result "SECRET_KEY" "OK" "Comprimento >= 32."
      } else {
        Add-Result "SECRET_KEY" "ALERTA" "Comprimento menor que 32."
      }
    } else {
      Add-Result "SECRET_KEY" "ALERTA" "SECRET_KEY nao encontrada no .env."
    }
  } else {
    Add-Result ".env" "ALERTA" "Arquivo .env nao encontrado."
  }
} catch {
  Add-Result "SECRET_KEY" "ERRO" $_.Exception.Message
}

try {
  $sqlitePath = Join-Path $ProjectDir "data\repoinvent.db"
  if (Test-Path -LiteralPath $sqlitePath) {
    $dbFile = Get-Item -LiteralPath $sqlitePath
    Add-Result "SQLite DB" "OK" ("Arquivo presente: {0} bytes" -f $dbFile.Length)
  } else {
    Add-Result "SQLite DB" "ALERTA" "Arquivo data\\repoinvent.db nao encontrado."
  }
} catch {
  Add-Result "SQLite DB" "ERRO" $_.Exception.Message
}

$reportDir = Join-Path $ProjectDir "logs"
if (!(Test-Path -LiteralPath $reportDir)) {
  New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}
$stamp = $now.ToString("yyyyMMdd-HHmmss")
$reportPath = Join-Path $reportDir ("healthcheck-mensal-{0}.txt" -f $stamp)

$header = @(
  "REPOINVENT - Healthcheck Mensal",
  "Data: $now",
  "Projeto: $rootDir",
  ""
)
$body = $results | ForEach-Object { "[{0}] {1} - {2}" -f $_.Status, $_.Item, $_.Details }
($header + $body) | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Output "Relatorio gerado em: $reportPath"
$results | Format-Table -AutoSize
