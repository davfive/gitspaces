@echo off
REM setup-venv.cmd
REM Windows cmd script for creating and configuring a Python virtual environment
setlocal enabledelayedexpansion

set "VENV_PATH=%~1"
if "%VENV_PATH%"=="" set "VENV_PATH=.venv"

set "REQUIREMENTS_FILE=%~2"

REM Because: Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
) else (
    echo Virtual environment already exists at %VENV_PATH%
)

REM Because: Activate and upgrade pip
call "%VENV_PATH%\Scripts\activate.bat"
python -m pip install --upgrade pip

REM Because: Install the package in editable mode (required for tests to import it)
python -m pip install -e .

REM Because: Install requirements if file is specified and exists
if not "%REQUIREMENTS_FILE%"=="" (
    if exist "%REQUIREMENTS_FILE%" (
        echo Installing dependencies from %REQUIREMENTS_FILE%...
        python -m pip install -r "%REQUIREMENTS_FILE%"
    )
)

REM Afterward: Virtual environment is ready for use
echo Virtual environment setup complete at %VENV_PATH%
endlocal
