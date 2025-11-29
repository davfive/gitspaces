#!/usr/bin/env bash
set -euo pipefail

# Test a PyPI release by installing it in a fresh venv
# Usage: ./scripts/test-pypi-release.sh [--tag TAG] [--target DIR] [--prod]

TAG=""
TARGET_DIR=""
USE_PROD=false

usage() {
  cat <<EOF
Usage: $0 [OPTIONS]

Test a PyPI release by installing it in a fresh virtual environment.

OPTIONS:
  --tag TAG        Version tag to test (e.g., v3.0.0-alpha.4)
  --target DIR     Directory to create venv in (default: tmp/test.pypi/TAG or tmp/pypi/TAG)
  --prod           Install from production PyPI instead of TestPyPI
  -h, --help       Show this help message

EXAMPLES:
  # Test from TestPyPI (default)
  $0 --tag v3.0.0-alpha.4

  # Test from production PyPI
  $0 --tag v3.0.0 --prod

  # Use custom directory
  $0 --tag v3.0.0-alpha.4 --target /tmp/my-test

EOF
  exit 0
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tag) TAG="$2"; shift 2 ;;
      --target) TARGET_DIR="$2"; shift 2 ;;
      --prod) USE_PROD=true; shift ;;
      -h|--help) usage ;;
      *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
  done

  if [[ -z "$TAG" ]]; then
    echo "Error: --tag is required" >&2
    echo "Run with --help for usage" >&2
    exit 1
  fi

  # Strip 'v' prefix for version
  VERSION="${TAG#v}"

  # Set default target directory if not provided
  if [[ -z "$TARGET_DIR" ]]; then
    if $USE_PROD; then
      TARGET_DIR="tmp/pypi/${TAG}"
    else
      TARGET_DIR="tmp/test.pypi/${TAG}"
    fi
  fi
}

create_venv() {
  echo "Creating virtual environment in: $TARGET_DIR"
  mkdir -p "$TARGET_DIR"
  python3 -m venv "$TARGET_DIR"
  # shellcheck source=/dev/null
  source "$TARGET_DIR/bin/activate"
  pip install -U pip
}

install_package() {
  if $USE_PROD; then
    echo "Installing gitspaces==${VERSION} from PyPI..."
    pip install "gitspaces==${VERSION}"
  else
    echo "Installing gitspaces==${VERSION} from TestPyPI..."
    pip install --index-url https://test.pypi.org/simple/ \
                --extra-index-url https://pypi.org/simple/ \
                "gitspaces==${VERSION}"
  fi
}

verify_installation() {
  echo ""
  echo "Verifying installation..."
  gitspaces --version
  echo ""
  echo "Installation successful!"
  echo ""
  echo "Virtual environment is at: $TARGET_DIR"
  echo "To activate: source $TARGET_DIR/bin/activate"
  echo "To test: gitspaces --help"
}

main() {
  parse_args "$@"
  create_venv
  install_package
  verify_installation
}

main "$@"
