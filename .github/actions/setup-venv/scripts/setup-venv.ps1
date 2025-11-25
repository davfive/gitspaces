# setup-venv.ps1
# PowerShell script for creating and configuring a Python virtual environment
param(
    [Parameter(Position=0)]
    [string]$VenvPath = ".venv",
    
    [Parameter(Position=1)]
    [string]$RequirementsFile = ""
)

$ErrorActionPreference = "Stop"

# Because: Create virtual environment if it doesn't exist
if (-not (Test-Path "$VenvPath\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment at $VenvPath..."
    python -m venv $VenvPath
} else {
    Write-Host "Virtual environment already exists at $VenvPath"
}

# Because: Activate and upgrade pip
& "$VenvPath\Scripts\Activate.ps1"
python -m pip install --upgrade pip

# Because: Install requirements if file is specified and exists
if ($RequirementsFile -and (Test-Path $RequirementsFile)) {
    Write-Host "Installing dependencies from $RequirementsFile..."
    python -m pip install -r $RequirementsFile
}

# Afterward: Virtual environment is ready for use
Write-Host "Virtual environment setup complete at $VenvPath"
