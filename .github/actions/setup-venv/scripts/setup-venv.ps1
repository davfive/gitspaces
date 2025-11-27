# setup-venv.ps1
# PowerShell script for creating and configuring a Python virtual environment
# Supports CI matrix jobs by creating a separate venv per Python version
param(
    [Parameter(Position=0)]
    [string]$VenvPathBase = ".venv",
    
    [Parameter(Position=1)]
    [string]$RequirementsFile = ""
)

$ErrorActionPreference = "Stop"

# Because: ensure that when matrix jobs run multiple Python versions on the same runner, each Python version gets an isolated venv
# Afterward: a venv directory named .venv-py<M>.<m> exists and its python matches the current interpreter
$PyVer = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$VenvPath = "$VenvPathBase-py$PyVer"

# Because: reuse a venv only when it already matches the interpreter version
# Afterward: existing venv is kept if it matches; otherwise it's removed so we recreate it
if (Test-Path "$VenvPath\Scripts\python.exe") {
    $ExistingVer = & "$VenvPath\Scripts\python.exe" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ($ExistingVer -ne $PyVer) {
        Write-Host "Existing venv python $ExistingVer does not match current python $PyVer; recreating $VenvPath"
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Write-Host "Using existing venv $VenvPath (python $ExistingVer)"
    }
} elseif (Test-Path $VenvPath) {
    Write-Host "Venv dir exists but no python binary found; recreating $VenvPath"
    Remove-Item -Recurse -Force $VenvPath
}

# Because: create a venv tied to the current python interpreter
# Afterward: $VenvPath exists
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment at $VenvPath..."
    python -m venv $VenvPath
}

# Because: Activate and upgrade pip
& "$VenvPath\Scripts\Activate.ps1"
python -m pip install --upgrade pip

# Because: Build and install the package as a wheel (faster and more representative of user installs)
# Afterward: the package wheel is installed and importable
Write-Host "Building package wheel..."
python -m pip install build
python -m build --wheel
Write-Host "Installing package wheel..."
$WheelFile = Get-ChildItem -Path "dist\*.whl" | Select-Object -First 1
python -m pip install $WheelFile.FullName

# Because: Install requirements if file is specified and exists
# Afterward: all dev dependencies are installed (local wheels first with fallback to index)
if ($RequirementsFile -and (Test-Path $RequirementsFile)) {
    Write-Host "Installing dependencies from $RequirementsFile..."
    # Try local wheels first if wheels directory exists
    if (Test-Path "wheels") {
        Write-Host "Attempting install from local wheels cache..."
        $localInstallResult = python -m pip install --no-index --find-links wheels/ -r $RequirementsFile 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully installed from local wheels"
        } else {
            Write-Host "Local wheels incomplete, falling back to index..."
            python -m pip install -r $RequirementsFile
        }
    } else {
        python -m pip install -r $RequirementsFile
    }
}

# Afterward: Virtual environment is ready for use
Write-Host "Virtual environment setup complete at $VenvPath"

# Export the actual venv path for callers that need it
$env:VENV_PATH = $VenvPath
