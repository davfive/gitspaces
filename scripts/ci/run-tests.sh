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

pip install -e .[dev]


# If UPLOAD_COVERAGE or TEST_COVERAGE_FILE is set, add coverage options
COVERAGE_ARGS=()
if [[ "${UPLOAD_COVERAGE:-}" == "true" || -n "${TEST_COVERAGE_FILE:-}" ]]; then
  COV_FILE="${TEST_COVERAGE_FILE:-coverage-$(python -c 'import sys; print(\"%d.%d\" % sys.version_info[:2])').xml}"
  COVERAGE_ARGS+=(--cov=src/gitspaces --cov-report=xml:"$COV_FILE" --cov-report=term)
fi

pytest "$@" "${COVERAGE_ARGS[@]}"