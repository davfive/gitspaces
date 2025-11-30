#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ ! -d "venv" ]; then
    python3 -m venv venv
  fi
  source venv/bin/activate
fi

pip install -e .
pip install -r requirements-dev.txt

RUN_SECURITY=true
if [[ "${1:-}" == "--quick" ]]; then
    RUN_SECURITY=false
fi

flake8 src/gitspaces
black --check src/gitspaces tests
mypy src/gitspaces

if [[ "$RUN_SECURITY" == "true" ]]; then
  if command -v pip-audit &> /dev/null; then pip-audit || true; fi
  if command -v bandit &> /dev/null; then bandit -r src/gitspaces -lll || true; fi
  if command -v semgrep &> /dev/null; then semgrep --config p/ci || true; fi
fi
