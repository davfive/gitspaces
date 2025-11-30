#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$PROJECT_ROOT"
echo "[run-tests] Running from: $(pwd)"

if [ -z "${VIRTUAL_ENV:-}" ]; then
  if [ ! -d "venv" ]; then
    python3 -m venv venv
  fi
  source venv/bin/activate
fi

pip install -e .
pip install -r requirements-dev.txt

pytest "$@"
