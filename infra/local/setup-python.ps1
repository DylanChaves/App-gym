$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $projectRoot
try {
    if (!(Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if (Test-Path -LiteralPath $bundledPython) { & $bundledPython -m venv .venv }
        elseif (Get-Command py -ErrorAction SilentlyContinue) { py -3.12 -m venv .venv }
        else { throw 'Instala Python 3.12 con su lanzador py o usa el entorno Python de Codex.' }
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear .venv. Comprueba que Python 3.12 esté instalado.' }
    }
    & '.\.venv\Scripts\python.exe' -m pip install -r backend\requirements\locked.txt
    if ($LASTEXITCODE -ne 0) { throw 'Falló la instalación de dependencias Python. Comprueba conectividad y el mensaje de pip.' }
} finally { Pop-Location }
