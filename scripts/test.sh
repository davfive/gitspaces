#!/usr/bin/env bash
set -euo pipefail

# Unified runner for tests and static checks
# Usage:
#   ./scripts/run.sh --tests         # Run tests only
#   ./scripts/run.sh --lint          # Run static checks only
#   ./scripts/run.sh --security      # Run static checks with security
#   ./scripts/run.sh --all           # Run both tests and static checks
#   ./scripts/run.sh --help          # Show help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RUN_TESTS=false
RUN_LINT=false
RUN_SECURITY=false

if [[ $# -eq 0 ]]; then
  RUN_TESTS=true
else
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tests) RUN_TESTS=true; shift ;;
      --lint) RUN_LINT=true; shift ;;
      --security) RUN_SECURITY=true; shift ;;
      --all) RUN_TESTS=true; RUN_LINT=true; shift ;;
      --help|-h)
        echo "Usage: $0 [--tests] [--lint] [--security] [--all]"
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        exit 1
        ;;
    esac
  done
fi

if $RUN_LINT; then
  if $RUN_SECURITY; then
    ./ci/static-checks.sh
  else
    ./ci/static-checks.sh --quick
  fi
fi

if $RUN_TESTS; then
  ./ci/run-tests.sh
fi
