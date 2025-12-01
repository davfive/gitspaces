# Shared static checks runner for local and CI (PowerShell)
# Usage: ./scripts/ci/static-checks.ps1 [--quick]

if (-not $env:VIRTUAL_ENV) {
  if (-not (Test-Path "venv")) {
    python -m venv venv
  }
  .\venv\Scripts\Activate.ps1
}

pip install -e .[dev]

$run_security = $true
if ($args[0] -eq "--quick") { $run_security = $false }


# Ruff/Black: lint or autofix
if ($args -contains "--fix") {
  Write-Host "[static-checks] Running autofix (black, ruff --fix)"
  black src/gitspaces tests
  ruff check src/gitspaces tests --fix
  ruff check --select I src/gitspaces tests --fix
} else {
  black --check src/gitspaces tests
  ruff check src/gitspaces tests
  ruff check --select I src/gitspaces tests
}
mypy src/gitspaces

if ($run_security) {
  try { pip-audit } catch { Write-Host "pip-audit not installed" }
  try { bandit -r src/gitspaces -lll } catch { Write-Host "bandit not installed" }
  try { semgrep --config p/ci } catch { Write-Host "semgrep not installed" }
}
