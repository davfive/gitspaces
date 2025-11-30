@echo off
REM Shared test runner for local and CI (cmd)
REM Usage: scripts\ci\run-tests.cmd [pytest args]

IF NOT DEFINED VIRTUAL_ENV (
  IF NOT EXIST venv (
    python -m venv venv
  )
  call venv\Scripts\activate.bat
)

pip install -e .
pip install -r requirements-dev.txt

pytest %*
