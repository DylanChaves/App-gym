param([ValidateSet('install','dev','lint','typecheck','build','build:pwa','test','test:e2e')][string]$Task = 'dev')
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$nodePath = (Get-Command node -ErrorAction SilentlyContinue).Source
$bundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
if ($nodePath) { $version = [version]((& $nodePath --version).TrimStart('v')) }
if (!$nodePath -or ($version.Major -eq 22 -and $version.Minor -lt 22) -or $version.Major -lt 22) {
    if (Test-Path -LiteralPath $bundledNode) { $nodePath = $bundledNode }
    else { throw 'Instala Node 24 LTS o Node 22.22 o superior.' }
}
$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (!$npmCommand) { throw 'npm.cmd no está instalado. Instala Node con npm.' }
$npmCli = Join-Path (Split-Path $npmCommand.Source) 'node_modules\npm\bin\npm-cli.js'
if (!(Test-Path -LiteralPath $npmCli)) { throw 'No se encuentra npm-cli.js junto a npm.cmd.' }
$previousPath = $env:Path
Push-Location (Join-Path $projectRoot 'frontend')
try {
    $env:Path = (Split-Path $nodePath) + ';' + $env:Path
    if ($Task -eq 'install') { & $nodePath $npmCli ci }
    else { & $nodePath $npmCli run $Task }
    if ($LASTEXITCODE -ne 0) { throw "Falló el comando frontend: $Task (código $LASTEXITCODE)." }
} finally { Pop-Location; $env:Path = $previousPath }
