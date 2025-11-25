#!/usr/bin/env bash
# Because: Cross-platform test runner for pyenv-based multi-version Python testing
# Supports: Linux, macOS, and WSL (bash shell)
# Usage: ./scripts/run-tests.sh [PYTHON_VERSION]
#   PYTHON_VERSION: Optional Python version (e.g., 3.13). If not provided, uses pyenv local version.
set -euo pipefail

PYTHON_VERSION="${1:-}"
COVERAGE_SUFFIX="${PYTHON_VERSION:-default}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Afterward: Change to project root
cd "$PROJECT_ROOT"

# Because: Detect if running in WSL
is_wsl() {
    grep -qiE "(microsoft|wsl)" /proc/version 2>/dev/null
}

# Because: Setup pyenv environment
setup_pyenv() {
    if [ -z "${PYENV_ROOT:-}" ]; then
        export PYENV_ROOT="$HOME/.pyenv"
    fi
    if [ -d "$PYENV_ROOT/bin" ]; then
        export PATH="$PYENV_ROOT/bin:$PATH"
    fi
    if command -v pyenv >/dev/null 2>&1; then
        eval "$(pyenv init -)"
    fi
}

# Because: Install Python version via pyenv if not available
install_python_version() {
    local version="$1"
    if ! pyenv versions --bare | grep -q "^${version}"; then
        echo "Installing Python ${version} via pyenv..."
        pyenv install "$version"
    fi
    pyenv local "$version"
    echo "Using Python $(python --version)"
}

# Because: Install dependencies
install_deps() {
    echo "Installing dependencies..."
    python -m pip install --upgrade pip setuptools wheel
    pip install -e .
    pip install -r requirements-dev.txt
}

# Because: Run linting checks (uses .flake8 config file for settings)
run_lint() {
    echo "Running flake8 linting..."
    flake8 src/gitspaces
    flake8 src/gitspaces --exit-zero

    echo "Checking code formatting with black..."
    black --check src/gitspaces tests
}

# Because: Run tests with coverage
run_tests() {
    echo "Running pytest with coverage..."
    pytest tests/ -v --cov=src/gitspaces --cov-report=xml:"coverage-${COVERAGE_SUFFIX}.xml" --cov-report=term
}

# Because: Main execution flow
main() {
    echo "=== Python Test Runner (bash) ==="
    echo "Python version requested: ${PYTHON_VERSION:-'(use local/default)'}"

    setup_pyenv

    if [ -n "$PYTHON_VERSION" ]; then
        if ! command -v pyenv >/dev/null 2>&1; then
            echo "Error: pyenv not found. Please install pyenv first."
            exit 1
        fi
        install_python_version "$PYTHON_VERSION"
    fi

    install_deps
    run_lint
    run_tests

    echo "=== Tests completed successfully ==="
    echo "Coverage report: coverage-${COVERAGE_SUFFIX}.xml"
}

main "$@"
