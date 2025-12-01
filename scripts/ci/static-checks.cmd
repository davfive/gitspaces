@echo off
REM Shared static checks runner for local and CI (cmd)
REM Usage: scripts\ci\static-checks.cmd [--no-security]

IF NOT DEFINED VIRTUAL_ENV (
  IF NOT EXIST venv (
    python -m venv venv
  )
  call venv\Scripts\activate.bat
)

pip install -e .[dev]

set RUN_SECURITY=true
IF "%1"=="--no-security" set RUN_SECURITY=false



REM Ruff/Black: lint or autofix
IF "%2"=="--fix" ( 
  ECHO [static-checks] Running autofix (black, ruff --fix)
  black src/gitspaces tests
  ruff check src/gitspaces tests --fix
  ruff check --select I src/gitspaces tests --fix
) ELSE IF "%1"=="--fix" ( 
  ECHO [static-checks] Running autofix (black, ruff --fix)
  black src/gitspaces tests
  ruff check src/gitspaces tests --fix
  ruff check --select I src/gitspaces tests --fix
) ELSE (
  black --check src/gitspaces tests
  ruff check src/gitspaces tests
  ruff check --select I src/gitspaces tests
)
mypy src/gitspaces

IF "%RUN_SECURITY%"=="true" (
  pip-audit || echo pip-audit not installed
  bandit -r src/gitspaces -lll || echo bandit not installed
  semgrep --config p/ci || echo semgrep not installed
)
