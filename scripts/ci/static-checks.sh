#!/usr/bin/env bash
set -euo pipefail


# Always cd to project root (git root) for pip install
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"
echo "[static-checks] Running from: $(pwd)"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ ! -d "venv" ]; then
    python3 -m venv venv
  fi
  source venv/bin/activate
fi

pip install -e .[dev]

RUN_SECURITY=true
if [[ "${1:-}" == "--quick" ]]; then
    RUN_SECURITY=false
fi



# Ruff/Black: lint or autofix
if [[ "${2:-}" == "--fix" || "${1:-}" == "--fix" ]]; then
  echo "[static-checks] Running autofix (ruff --fix, black)"
  ruff check src/gitspaces tests --fix
  ruff check --select I src/gitspaces tests --fix
  black src/gitspaces tests
else
  ruff check src/gitspaces tests
  ruff check --select I src/gitspaces tests
  black --check src/gitspaces tests
fi

# Mypy: type checking
mypy src/gitspaces

if [[ "$RUN_SECURITY" == "true" ]]; then
  if command -v pip-audit &> /dev/null; then pip-audit || true; fi
  if command -v bandit &> /dev/null; then bandit -r src/gitspaces -lll || true; fi
  if command -v semgrep &> /dev/null; then semgrep --config p/ci || true; fi
fi
