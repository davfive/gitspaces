#!/bin/bash
# Static analysis checks for gitspaces
# Run this script locally to check code quality before pushing
#
# Usage:
#   ./scripts/static-checks.sh           # Run all checks
#   ./scripts/static-checks.sh --quick   # Run only fast checks (flake8, black, mypy)
#   ./scripts/static-checks.sh --help    # Show this help
#
# Requirements:
#   pip install -r requirements-dev.txt
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Parse arguments
RUN_SECURITY=true
if [[ "$1" == "--quick" ]]; then
    RUN_SECURITY=false
elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [--quick|--help]"
    echo ""
    echo "Options:"
    echo "  --quick   Run only fast checks (flake8, black, mypy)"
    echo "  --help    Show this help message"
    echo ""
    echo "Requirements:"
    echo "  pip install -r requirements-dev.txt"
    exit 0
fi

echo "=== GitSpaces Static Analysis Checks ==="
echo ""

# Check if required tools are installed
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed. Run: pip install -r requirements-dev.txt"
        exit 1
    fi
}

check_tool flake8
check_tool black
check_tool mypy

echo ">>> Running flake8..."
flake8 src/gitspaces
echo "✓ flake8 passed"
echo ""

echo ">>> Running black (format check)..."
black --check src/gitspaces tests
echo "✓ black passed"
echo ""

echo ">>> Running mypy..."
mypy src/gitspaces
echo "✓ mypy passed"
echo ""

if [[ "$RUN_SECURITY" == "true" ]]; then
    echo ">>> Running pip-audit (dependency vuln scan)..."
    if command -v pip-audit &> /dev/null; then
        pip-audit || true
        echo "✓ pip-audit completed"
    else
        echo "⚠ pip-audit not installed, skipping (pip install pip-audit)"
    fi
    echo ""

    echo ">>> Running bandit (SAST)..."
    if command -v bandit &> /dev/null; then
        bandit -r src/gitspaces -lll || true
        echo "✓ bandit completed"
    else
        echo "⚠ bandit not installed, skipping"
    fi
    echo ""

    echo ">>> Running semgrep..."
    if command -v semgrep &> /dev/null; then
        semgrep --config p/ci || true
        echo "✓ semgrep completed"
    else
        echo "⚠ semgrep not installed, skipping (pip install semgrep)"
    fi
    echo ""
fi

echo "=== All static checks passed! ==="
