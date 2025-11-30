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


# Ruff: lint and import sort (auto-fix with --fix if desired)
ruff check src/gitspaces tests
ruff check --select I src/gitspaces tests

# Black: code formatting check
black --check src/gitspaces tests

# Mypy: type checking
mypy src/gitspaces

if [[ "$RUN_SECURITY" == "true" ]]; then
  if command -v pip-audit &> /dev/null; then pip-audit || true; fi
  if command -v bandit &> /dev/null; then bandit -r src/gitspaces -lll || true; fi
  if command -v semgrep &> /dev/null; then semgrep --config p/ci || true; fi
fi
