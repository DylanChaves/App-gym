param([string]$MySqlBin = 'C:\Program Files\MySQL\MySQL Server 8.0\bin')
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$localDir = Join-Path $projectRoot '.local'
$dataDir = Join-Path $localDir 'mysql-data'
$envFile = Join-Path $projectRoot 'backend\.env'
$credentialsFile = Join-Path $localDir 'mysql-credentials.json'
$markerFile = Join-Path $localDir 'mysql-ready'
$pidFile = Join-Path $localDir 'mysql.pid'
$server = Join-Path $MySqlBin 'mysqld.exe'
$client = Join-Path $MySqlBin 'mysql.exe'
if (!(Test-Path -LiteralPath $server) -or !(Test-Path -LiteralPath $client)) {
    throw "No se encuentran los binarios de MySQL en $MySqlBin. Usa -MySqlBin con la ruta correcta."
}
New-Item -ItemType Directory -Force -Path $localDir | Out-Null
if (!(Test-Path -LiteralPath $credentialsFile)) {
    if (Test-Path -LiteralPath $envFile) {
        throw 'backend/.env ya existe. No se sobrescribe. Configura tu MySQL existente o conserva ese archivo antes de usar esta instancia aislada.'
    }
    $credentials = @{
        root = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
        app = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
        secret = [Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(48))
    }
    $credentials | ConvertTo-Json | Set-Content -LiteralPath $credentialsFile -Encoding utf8
    @"
DJANGO_SECRET_KEY=$($credentials.secret)
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:9000,http://localhost:9000
MYSQL_DATABASE=gym_development
MYSQL_TEST_DATABASE=gym_test
MYSQL_USER=gym_app
MYSQL_PASSWORD=$($credentials.app)
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
REGISTRATION_ENABLED=false
"@ | Set-Content -LiteralPath $envFile -Encoding utf8NoBOM
}
$credentials = Get-Content -LiteralPath $credentialsFile -Raw | ConvertFrom-Json
if (!(Test-Path -LiteralPath (Join-Path $dataDir 'mysql'))) {
    New-Item -ItemType Directory -Force -Path $dataDir | Out-Null
    & $server --no-defaults --initialize-insecure "--datadir=$dataDir" --console
    if ($LASTEXITCODE -ne 0) { throw 'Falló la inicialización de MySQL. Consulta la salida anterior.' }
}
$running = $false
if (Test-Path -LiteralPath $pidFile) {
    $serverPid = [int](Get-Content -LiteralPath $pidFile)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $serverPid"
    $running = $process -and $process.ExecutablePath -eq $server -and $process.CommandLine.Contains($dataDir)
}
if (!$running) {
    $portUsed = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
    if ($portUsed) { throw 'El puerto 3307 está ocupado por otro proceso. No se modifica ese proceso.' }
    Start-Process -FilePath $server -ArgumentList @(
        '--no-defaults', ('--datadir="' + $dataDir + '"'), '--port=3307', '--bind-address=127.0.0.1',
        '--mysqlx=OFF', '--character-set-server=utf8mb4', '--collation-server=utf8mb4_unicode_ci',
        ('--pid-file="' + $pidFile + '"'), ('--log-error="' + (Join-Path $localDir 'mysql.log') + '"')
    ) -WindowStyle Hidden | Out-Null
}
$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    $connection = [Net.Sockets.TcpClient]::new()
    try { $connection.Connect('127.0.0.1', 3307); $ready = $true } catch { Start-Sleep -Seconds 1 }
    finally { $connection.Dispose() }
    if ($ready) { break }
}
if (!$ready) { throw 'MySQL no inició en 30 segundos. Consulta .local/mysql.log.' }
if (!(Test-Path -LiteralPath $markerFile)) {
    # Credentials are random hex, never printed, never passed in process arguments.
    @"
CREATE DATABASE IF NOT EXISTS gym_development CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS gym_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'gym_app'@'127.0.0.1' IDENTIFIED BY '$($credentials.app)';
GRANT ALL PRIVILEGES ON gym_development.* TO 'gym_app'@'127.0.0.1';
GRANT ALL PRIVILEGES ON gym_test.* TO 'gym_app'@'127.0.0.1';
ALTER USER 'root'@'localhost' IDENTIFIED BY '$($credentials.root)';
"@ | & $client --no-defaults --host=127.0.0.1 --port=3307 --user=root
    if ($LASTEXITCODE -ne 0) { throw 'Falló la configuración de cuentas y bases. No se ha marcado como completada.' }
    'ready' | Set-Content -LiteralPath $markerFile
}
Write-Output 'MySQL aislado listo en 127.0.0.1:3307. backend/.env contiene la configuración local; no publiques ese archivo.'
