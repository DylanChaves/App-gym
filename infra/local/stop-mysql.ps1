param([string]$MySqlBin = 'C:\Program Files\MySQL\MySQL Server 8.0\bin')
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$credentials = Get-Content -LiteralPath (Join-Path $projectRoot '.local\mysql-credentials.json') -Raw | ConvertFrom-Json
$previousPassword = $env:MYSQL_PWD
try {
    $env:MYSQL_PWD = $credentials.root
    & (Join-Path $MySqlBin 'mysqladmin.exe') --no-defaults --host=127.0.0.1 --port=3307 --user=root shutdown
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo detener la instancia aislada.' }
} finally { $env:MYSQL_PWD = $previousPassword }
$pidFile = Join-Path $projectRoot '.local\mysql.pid'
# mysqladmin may return before mysqld removes its PID file. Wait for shutdown
# to finish so an immediate start cannot mistake the old process for a live server.
for ($attempt = 0; $attempt -lt 30 -and (Test-Path -LiteralPath $pidFile); $attempt++) {
    Start-Sleep -Seconds 1
}
if (Test-Path -LiteralPath $pidFile) { throw 'MySQL no completó el cierre en 30 segundos. Consulta .local/mysql.log.' }
Write-Output 'Instancia MySQL aislada detenida de forma ordenada.'
