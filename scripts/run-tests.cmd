@echo off
REM Because: Cross-platform test runner wrapper for Windows CMD
REM Supports: Windows CMD with pyenv-win (delegates to PowerShell script)
REM Usage: scripts\run-tests.cmd [PYTHON_VERSION]
REM   PYTHON_VERSION: Optional Python version (e.g., 3.13). If not provided, uses pyenv local version.

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON_VERSION=%~1"

REM Afterward: Delegate to PowerShell script with the same arguments
if "%PYTHON_VERSION%"=="" (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run-tests.ps1"
) else (
    powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run-tests.ps1" -PythonVersion "%PYTHON_VERSION%"
)

exit /b %ERRORLEVEL%
