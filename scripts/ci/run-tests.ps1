# Shared test runner for local and CI (PowerShell)
# Usage: ./scripts/ci/run-tests.ps1 [pytest args]

if (-not $env:VIRTUAL_ENV) {
  if (-not (Test-Path "venv")) {
    python -m venv venv
  }
  .\venv\Scripts\Activate.ps1
}

pip install -e .
pip install -r requirements-dev.txt

pytest $args
