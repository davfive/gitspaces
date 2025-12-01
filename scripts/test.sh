#!/usr/bin/env bash
set -euo pipefail


# Unified runner for tests and static checks
# Usage:
#   ./scripts/test.sh --tests            # Run tests only
#   ./scripts/test.sh --lint             # Run static checks only
#   ./scripts/test.sh --security         # Run static checks with security
#   ./scripts/test.sh --no-security      # Run static checks without security
#   ./scripts/test.sh --all              # Run both tests and static checks
#   ./scripts/test.sh --fix              # Autofix lint/format issues (with --lint/--all)
#   ./scripts/test.sh --help             # Show help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"



RUN_TESTS=false
RUN_LINT=false
RUN_SECURITY=false
RUN_FIX=false


if [[ $# -eq 0 ]]; then
  RUN_TESTS=true
else
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tests) RUN_TESTS=true; shift ;;
      --lint) RUN_LINT=true; shift ;;
      --security) RUN_SECURITY=true; shift ;;
      --all) RUN_TESTS=true; RUN_LINT=true; shift ;;
      --fix) RUN_FIX=true; shift ;;
      --no-security) RUN_SECURITY=false; shift ;;
      --help|-h)
        echo "Usage: $0 [--tests] [--lint] [--security] [--no-security] [--all] [--fix]"
        echo "  --fix: Autofix lint/format issues (with --lint/--all)"
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
  STATIC_CHECKS_ARGS=()
  if $RUN_SECURITY; then
    STATIC_CHECKS_ARGS+=(--security)
  else
    STATIC_CHECKS_ARGS+=(--no-security)
  fi
  if $RUN_FIX; then
    STATIC_CHECKS_ARGS+=(--fix)
  fi
  ./ci/static-checks.sh "${STATIC_CHECKS_ARGS[@]}"
fi

if $RUN_TESTS; then
  ./ci/run-tests.sh
fi
