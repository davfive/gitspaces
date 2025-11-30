# Shared test runner for local and CI (PowerShell)
# Usage: ./scripts/ci/run-tests.ps1 [pytest args]

if (-not $env:VIRTUAL_ENV) {
  if (-not (Test-Path "venv")) {
    python -m venv venv
  }
  .\venv\Scripts\Activate.ps1
}

# Change to project root (git root if available)
$projectRoot = $(git rev-parse --show-toplevel 2>$null)
if (-not $projectRoot) {
  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
  $projectRoot = Join-Path $scriptDir '..'
}
Set-Location $projectRoot
Write-Host "[run-tests] Running from: $(Get-Location)"

pip install -e .
pip install -r requirements-dev.txt

pytest $args
