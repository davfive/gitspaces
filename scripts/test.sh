#!/usr/bin/env bash
set -euo pipefail

# Run tests and static checks for gitspaces
# Usage:
#   ./scripts/test.sh                    # Run all tests
#   ./scripts/test.sh --cov              # Run with coverage report
#   ./scripts/test.sh --lint             # Run static checks (flake8, black, mypy)
#   ./scripts/test.sh --all              # Run tests + static checks
#   ./scripts/test.sh --file <path>      # Run specific test file
#   ./scripts/test.sh --quick            # Run without verbose output
#   ./scripts/test.sh --help             # Show this help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Detect or setup venv
setup_venv() {
  if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "No active virtual environment detected."
    if [ ! -d "venv" ]; then
      echo "Creating venv..."
      python3 -m venv venv
    fi
    echo "Activating venv..."
    # shellcheck source=/dev/null
    source venv/bin/activate
    
    # Install dependencies if needed
    if ! python -c "import pytest" 2>/dev/null; then
      echo "Installing dependencies..."
      pip install -q -e .
      pip install -q -r requirements-dev.txt
    fi
  fi
}

run_static_checks() {
  local run_security="$1"
  
  echo "=== Running Static Checks ==="
  echo ""
  
  # Check if required tools are installed
  check_tool() {
    if ! command -v "$1" &> /dev/null && ! python -c "import $1" 2>/dev/null; then
      echo "⚠ $1 not installed, skipping"
      return 1
    fi
    return 0
  }
  
  if check_tool flake8; then
    echo ">>> Running flake8..."
    flake8 src/gitspaces
    echo "✓ flake8 passed"
    echo ""
  fi
  
  if check_tool black; then
    echo ">>> Running black (format check)..."
    black --check src/gitspaces tests
    echo "✓ black passed"
    echo ""
  fi
  
  if check_tool mypy; then
    echo ">>> Running mypy..."
    mypy src/gitspaces
    echo "✓ mypy passed"
    echo ""
  fi
  
  if [[ "$run_security" == "true" ]]; then
    if check_tool pip-audit; then
      echo ">>> Running pip-audit (dependency vuln scan)..."
      pip-audit || true
      echo "✓ pip-audit completed"
      echo ""
    fi
    
    if check_tool bandit; then
      echo ">>> Running bandit (SAST)..."
      bandit -r src/gitspaces -lll || true
      echo "✓ bandit completed"
      echo ""
    fi
    
    if check_tool semgrep; then
      echo ">>> Running semgrep..."
      semgrep --config p/ci || true
      echo "✓ semgrep completed"
      echo ""
    fi
  fi
  
  echo "=== Static checks completed ==="
  echo ""
}

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Run pytest tests and/or static checks for the gitspaces project.

OPTIONS:
  --cov           Run with coverage report (HTML output in htmlcov/)
  --lint          Run static checks only (flake8, black, mypy)
  --all           Run both tests and static checks
  --file PATH     Run specific test file
  --quick, -q     Run without verbose output
  --security      Include security checks (pip-audit, bandit, semgrep)
  --help, -h      Show this help message

EXAMPLES:
  # Run all tests with verbose output
  $0

  # Run with coverage
  $0 --cov

  # Run static checks
  $0 --lint

  # Run everything
  $0 --all

  # Run specific test file
  $0 --file tests/test_cmd_switch_integration.py

  # Quick run
  $0 -q

EOF
  exit 0
}

# Parse arguments
COVERAGE=false
VERBOSE="-v"
TEST_FILE=""
RUN_LINT=false
RUN_TESTS=true
RUN_SECURITY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cov) COVERAGE=true; shift ;;
    --lint) RUN_LINT=true; RUN_TESTS=false; shift ;;
    --all) RUN_LINT=true; RUN_TESTS=true; shift ;;
    --file) TEST_FILE="$2"; shift 2 ;;
    --quick|-q) VERBOSE="-q"; shift ;;
    --security) RUN_SECURITY=true; shift ;;
    --help|-h) usage ;;
    *) echo "Unknown option: $1" >&2; usage ;;
  esac
done

# Setup environment
setup_venv

# Run static checks if requested
if $RUN_LINT; then
  run_static_checks "$RUN_SECURITY"
fi

# Run tests if requested
if $RUN_TESTS; then
  echo "=== Running GitSpaces Tests ==="
  echo ""
  
  # Build pytest command
  PYTEST_CMD="pytest $VERBOSE"
  
  if $COVERAGE; then
    PYTEST_CMD="$PYTEST_CMD --cov=gitspaces --cov-report=html --cov-report=term"
  fi
  
  if [[ -n "$TEST_FILE" ]]; then
    PYTEST_CMD="$PYTEST_CMD $TEST_FILE"
  fi
  
  # Run tests
  echo "Command: $PYTEST_CMD"
  echo ""
  eval "$PYTEST_CMD"
  
  if $COVERAGE; then
    echo ""
    echo "Coverage report generated in htmlcov/index.html"
  fi
fi
