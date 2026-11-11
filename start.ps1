# Start this checkout using its virtual environment and private server settings.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $projectPython)) { throw 'Run .\setup.ps1 first.' }
    & $projectPython scripts/check_setup.py --startup-only
    if ($LASTEXITCODE -ne 0) { throw 'Startup checks failed. Run .\setup.ps1.' }
    & $projectPython app.py
    if ($LASTEXITCODE -ne 0) { throw 'The application stopped with an error.' }
} finally {
    Pop-Location
}
