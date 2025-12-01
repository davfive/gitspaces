# Unified runner for tests and static checks (PowerShell)
# Usage:
#   ./scripts/run.ps1 --tests
#   ./scripts/run.ps1 --lint
#   ./scripts/run.ps1 --security
#   ./scripts/run.ps1 --all

param(
  [switch]$tests,
  [switch]$lint,
  [switch]$security,
  [switch]$all,
  [switch]$help
)

if ($help) {
  Write-Host "Usage: run.ps1 [--tests] [--lint] [--security] [--all]"
  exit 0
}

$run_tests = $false
$run_lint = $false
$run_security = $false

if ($PSBoundParameters.Count -eq 0) {
  $run_tests = $true
}
if ($tests) { $run_tests = $true }
if ($lint) { $run_lint = $true }
if ($security) { $run_security = $true }
if ($all) { $run_tests = $true; $run_lint = $true }

if ($run_lint) {
  if ($run_security) {
    .\ci\static-checks.ps1
  } else {
    .\ci\static-checks.ps1 --no-security
  }
}
if ($run_tests) {
  .\ci\run-tests.ps1
}
