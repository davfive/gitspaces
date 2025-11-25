#!/usr/bin/env bash
# Usage: ./scripts/run-tests.sh "3.9,3.10,3.11"
# Portable: try to enable pipefail if supported; fall back silently if not.
set -euo pipefail 2>/dev/null || { set -euo; }

VERSIONS_STR="${1:-3.13}"
# normalize to space-separated list
VERSIONS="$(echo "$VERSIONS_STR" | tr -d ' ' | tr ',' ' ')"

# Ensure pyenv prerequisites on Debian/Ubuntu. (On macOS use brew: see README)
if [ -f /etc/debian_version ]; then
  sudo apt-get update -y
  sudo apt-get install -y --no-install-recommends \
    make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils \
    tk-dev libffi-dev liblzma-dev git
fi

# Install pyenv if missing
if [ ! -d "${HOME}/.pyenv" ]; then
  echo "Installing pyenv..."
  curl https://pyenv.run | bash
fi

export PYENV_ROOT="${HOME}/.pyenv"
export PATH="${PYENV_ROOT}/bin:${PATH}"
# shellcheck disable=SC1090
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)" || true

echo "Testing Python versions: $VERSIONS"
LINT_DONE=0
FAILED=0

for ver in $VERSIONS; do
  echo "=== Ensuring Python $ver ==="
  pyenv install -s "$ver"
  pyenv shell "$ver"

  VENV_DIR=".venv-$ver"
  echo "=== Creating venv $VENV_DIR ==="
  python -m venv "$VENV_DIR"
  PY="$VENV_DIR/bin/python"
  PIP="$VENV_DIR/bin/pip"

  "$PY" -m pip install --upgrade pip setuptools wheel
  if ! "$PIP" install -e . -r requirements-dev.txt; then
    echo "pip install failed for $ver" >&2
    FAILED=1
  fi

  if [ "$LINT_DONE" -eq 0 ]; then
    echo "=== Running lint & black (once) with $ver ==="
    "$PIP" install flake8 black
    if ! "$PY" -m flake8 src/gitspaces --count --select=E9,F63,F7,F82 --show-source --statistics; then
      echo "flake8 found errors" >&2
      FAILED=1
    fi
    # optional non-fatal flake8 pass
    "$PY" -m flake8 src/gitspaces --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || true
    if ! "$PY" -m black --check src/gitspaces tests; then
      echo "black check failed" >&2
      FAILED=1
    fi
    LINT_DONE=1
  fi

  echo "=== Running tests for $ver ==="
  COV_FILE="coverage-${ver}.xml"
  if ! "$PY" -m pytest tests/ -v --cov=src/gitspaces --cov-report=xml:$COV_FILE --cov-report=term; then
    echo "pytest failed for $ver" >&2
    FAILED=1
  fi
done

if [ "$FAILED" -ne 0 ]; then
  echo "One or more python-version runs failed." >&2
  exit 1
fi

echo "All runs passed."