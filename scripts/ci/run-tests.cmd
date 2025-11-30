@echo off
REM Shared test runner for local and CI (cmd)
REM Usage: scripts\ci\run-tests.cmd [pytest args]

IF NOT DEFINED VIRTUAL_ENV (
  IF NOT EXIST venv (
    python -m venv venv
  )
  call venv\Scripts\activate.bat
)

REM Change to project root (git root if available)
FOR /F "delims=" %%i IN ('git rev-parse --show-toplevel 2^>NUL') DO SET PROJECT_ROOT=%%i
IF DEFINED PROJECT_ROOT (
  CD /D "%PROJECT_ROOT%"
) ELSE (
  CD /D "%~dp0.."
)
echo [run-tests] Running from: %CD%

pip install -e .
pip install -r requirements-dev.txt

pytest %*
