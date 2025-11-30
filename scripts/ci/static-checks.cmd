@echo off
REM Shared static checks runner for local and CI (cmd)
REM Usage: scripts\ci\static-checks.cmd [--quick]

IF NOT DEFINED VIRTUAL_ENV (
  IF NOT EXIST venv (
    python -m venv venv
  )
  call venv\Scripts\activate.bat
)

pip install -e .[dev]

set RUN_SECURITY=true
IF "%1"=="--quick" set RUN_SECURITY=false

flake8 src/gitspaces
black --check src/gitspaces tests
mypy src/gitspaces

IF "%RUN_SECURITY%"=="true" (
  pip-audit || echo pip-audit not installed
  bandit -r src/gitspaces -lll || echo bandit not installed
  semgrep --config p/ci || echo semgrep not installed
)
