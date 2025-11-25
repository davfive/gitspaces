# Because: Cross-platform test runner for pyenv-win based multi-version Python testing on Windows
# Supports: Windows PowerShell with pyenv-win
# Usage: .\scripts\run-tests.ps1 [-PythonVersion <version>]
#   -PythonVersion: Optional Python version (e.g., 3.13). If not provided, uses pyenv local version.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$PythonVersion = ""
)

$ErrorActionPreference = "Stop"

$CoverageSuffix = if ($PythonVersion) { $PythonVersion } else { "default" }
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Afterward: Change to project root
Set-Location $ProjectRoot

# Because: Setup pyenv-win environment
function Setup-PyenvWin {
    $pyenvRoot = $env:PYENV_ROOT
    if (-not $pyenvRoot) {
        $pyenvRoot = "$env:USERPROFILE\.pyenv\pyenv-win"
        $env:PYENV_ROOT = $pyenvRoot
    }
    
    $pyenvBin = "$pyenvRoot\bin"
    $pyenvShims = "$pyenvRoot\shims"
    
    if (Test-Path $pyenvBin) {
        $env:PATH = "$pyenvBin;$pyenvShims;$env:PATH"
    }
}

# Because: Install Python version via pyenv-win if not available
function Install-PythonVersion {
    param([string]$Version)
    
    $installedVersions = & pyenv versions --bare 2>$null
    if ($installedVersions -notcontains $Version) {
        Write-Host "Installing Python $Version via pyenv-win..."
        & pyenv install $Version
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install Python $Version"
        }
    }
    
    & pyenv local $Version
    Write-Host "Using Python $(& python --version)"
}

# Because: Install dependencies
function Install-Dependencies {
    Write-Host "Installing dependencies..."
    & python -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) { throw "Failed to upgrade pip" }
    
    & pip install -e .
    if ($LASTEXITCODE -ne 0) { throw "Failed to install package" }
    
    & pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Failed to install dev requirements" }
}

# Because: Run linting checks
function Run-Lint {
    Write-Host "Running flake8 linting..."
    & flake8 src/gitspaces --count --select=E9,F63,F7,F82 --show-source --statistics
    if ($LASTEXITCODE -ne 0) { throw "Flake8 found critical errors" }
    
    & flake8 src/gitspaces --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    Write-Host "Checking code formatting with black..."
    & black --check src/gitspaces tests
    if ($LASTEXITCODE -ne 0) { throw "Black formatting check failed" }
}

# Because: Run tests with coverage
function Run-Tests {
    Write-Host "Running pytest with coverage..."
    & pytest tests/ -v --cov=src/gitspaces --cov-report=xml:"coverage-$CoverageSuffix.xml" --cov-report=term
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
}

# Because: Main execution flow
function Main {
    Write-Host "=== Python Test Runner (PowerShell) ==="
    Write-Host "Python version requested: $(if ($PythonVersion) { $PythonVersion } else { '(use local/default)' })"
    
    Setup-PyenvWin
    
    if ($PythonVersion) {
        $pyenvCmd = Get-Command pyenv -ErrorAction SilentlyContinue
        if (-not $pyenvCmd) {
            throw "pyenv-win not found. Please install pyenv-win first."
        }
        Install-PythonVersion -Version $PythonVersion
    }
    
    Install-Dependencies
    Run-Lint
    Run-Tests
    
    Write-Host "=== Tests completed successfully ==="
    Write-Host "Coverage report: coverage-$CoverageSuffix.xml"
}

Main
