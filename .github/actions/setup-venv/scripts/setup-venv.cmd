@echo off
REM setup-venv.cmd
REM Windows cmd script for creating and configuring a Python virtual environment
REM Supports CI matrix jobs by creating a separate venv per Python version
setlocal enabledelayedexpansion

set "VENV_PATH_BASE=%~1"
if "%VENV_PATH_BASE%"=="" set "VENV_PATH_BASE=.venv"

set "REQUIREMENTS_FILE=%~2"

REM Because: ensure that when matrix jobs run multiple Python versions on the same runner, each Python version gets an isolated venv
REM Afterward: a venv directory named .venv-py<M>.<m> exists and its python matches the current interpreter
for /f "delims=" %%V in ('python -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))"') do set "PY_VER=%%V"
set "VENV_PATH=%VENV_PATH_BASE%-py%PY_VER%"

REM Because: reuse a venv only when it already matches the interpreter version
REM Afterward: existing venv is kept if it matches; otherwise it's removed so we recreate it
if exist "%VENV_PATH%\Scripts\python.exe" (
    for /f "delims=" %%E in ('"%VENV_PATH%\Scripts\python.exe" -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))"') do set "EXISTING_VER=%%E"
    if not "!EXISTING_VER!"=="%PY_VER%" (
        echo Existing venv python !EXISTING_VER! does not match current python %PY_VER%; recreating %VENV_PATH%
        rmdir /s /q "%VENV_PATH%"
    ) else (
        echo Using existing venv %VENV_PATH% ^(python !EXISTING_VER!^)
    )
) else if exist "%VENV_PATH%" (
    echo Venv dir exists but no python binary found; recreating %VENV_PATH%
    rmdir /s /q "%VENV_PATH%"
)

REM Because: create a venv tied to the current python interpreter
REM Afterward: %VENV_PATH% exists
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
)

REM Because: Activate and upgrade pip
call "%VENV_PATH%\Scripts\activate.bat"
python -m pip install --upgrade pip

REM Because: Build and install the package as a wheel (faster and more representative of user installs)
REM Afterward: the package wheel is installed and importable
echo Building package wheel...
python -m pip install build
python -m build --wheel
echo Installing package wheel...
for %%W in (dist\*.whl) do python -m pip install "%%W"

REM Because: Install requirements if file is specified and exists
REM Afterward: all dev dependencies are installed (local wheels first with fallback to index)
if not "%REQUIREMENTS_FILE%"=="" (
    if exist "%REQUIREMENTS_FILE%" (
        echo Installing dependencies from %REQUIREMENTS_FILE%...
        REM Try local wheels first if wheels directory exists
        if exist "wheels" (
            echo Attempting install from local wheels cache...
            python -m pip install --no-index --find-links wheels/ -r "%REQUIREMENTS_FILE%" 2>nul
            if errorlevel 1 (
                echo Local wheels incomplete, falling back to index...
                python -m pip install -r "%REQUIREMENTS_FILE%"
            ) else (
                echo Successfully installed from local wheels
            )
        ) else (
            python -m pip install -r "%REQUIREMENTS_FILE%"
        )
    )
)

REM Afterward: Virtual environment is ready for use
echo Virtual environment setup complete at %VENV_PATH%
endlocal & set "VENV_PATH=%VENV_PATH%"
