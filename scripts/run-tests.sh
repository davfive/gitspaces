#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/run-tests.py"
VERSIONS="${1:-}"

PY_CMD=python
if ! command -v python >/dev/null 2>&1; then
  if command -v py >/dev/null 2>&1; then
    PY_CMD="py -3"
  else
    echo "ERROR: No python interpreter found on PATH." >&2
    exit 1
  fi
fi

if [ -z "$VERSIONS" ]; then
  $PY_CMD "$PY_SCRIPT"
else
  $PY_CMD "$PY_SCRIPT" "$VERSIONS"
fi