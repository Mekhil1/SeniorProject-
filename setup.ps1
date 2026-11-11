# Prepare this checkout only. Never changes system settings or cloud resources.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'
        if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 or newer first (3.12 recommended).' }
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv.' }
    }
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    & $projectPython -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'
    if ($LASTEXITCODE -ne 0) { throw 'This .venv needs Python 3.11 or newer. Preserve it and create a compatible environment.' }
    & $projectPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed; do not ignore this error.' }
    & $projectPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency conflicts detected.' }
    & $projectPython scripts/configure_local.py
    if ($LASTEXITCODE -ne 0) { throw 'Local configuration could not be prepared.' }
    & $projectPython scripts/check_setup.py --startup-only
    if ($LASTEXITCODE -ne 0) { throw 'Startup checks failed.' }
    Write-Output 'Enter your keys privately in .env, then run .\start.ps1.'
} finally {
    Pop-Location
}
