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

pytest "$@"
