#!/usr/bin/env bash
set -euxo pipefail

# Globals
PUSH=false
REMOTE="origin"
MODE=""          # "", "editor", or "stdin" (defaults to "stdin" if unset)
EXPLICIT_TAG=""

SEMVER_TAG_RE='^v([0-9]+)\.([0-9]+)\.([0-9]+)(-[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?$'

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --push) PUSH=true; shift ;;
      --remote) REMOTE="$2"; shift 2 ;;
      --editor) MODE="editor"; shift ;;
      --stdin) MODE="stdin"; shift ;;
      --tag) EXPLICIT_TAG="$2"; shift 2 ;;
      *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
  done
  # Default to stdin if neither editor nor stdin specified
  if [[ -z "$MODE" ]]; then
    MODE="stdin"
  fi
}

check_branch_clean() {
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "$branch" != "main" ]]; then
    echo "Must run release.sh from main. Current: $branch" >&2
    exit 1
  fi
  test -z "$(git status --porcelain)" || { echo "Working tree not clean"; exit 1; }
}

compute_next_tag() {
  # Find the latest tag by version sort
  local last_tag
  last_tag="$(git tag --list 'v*' | sort -V | tail -n1 || true)"
  if [[ -z "$last_tag" ]]; then
    echo "No existing tags found. Provide --tag vMAJOR.MINOR.PATCH[-pre]" >&2
    exit 1
  fi
  if [[ ! "$last_tag" =~ $SEMVER_TAG_RE ]]; then
    echo "Last tag '$last_tag' does not match expected pattern." >&2
    exit 1
  fi
  local major="${BASH_REMATCH[1]}"
  local minor="${BASH_REMATCH[2]}"
  local patch="${BASH_REMATCH[3]}"
  local prere="${BASH_REMATCH[4]}" # includes leading - if present

  if [[ -n "$prere" ]]; then
    # If prerelease ends with .N -> increment N; otherwise add .1
    if [[ "$prere" =~ ^-([0-9A-Za-z]+)\.([0-9]+)$ ]]; then
      local label="${BASH_REMATCH[1]}"
      local n="${BASH_REMATCH[2]}"
      echo "v${major}.${minor}.${patch}-${label}.$((n+1))"
    else
      echo "v${major}.${minor}.${patch}${prere}.1"
    fi
  else
    echo "v${major}.${minor}.$((patch+1))"
  fi
}

determine_tag() {
  if [[ -n "$EXPLICIT_TAG" ]]; then
    TAG="$EXPLICIT_TAG"
  else
    TAG="$(compute_next_tag)"
  fi
}

confirm_tag() {
  echo "Computed tag: $TAG"
  read -r -p "Is this tag correct? [y/N] " CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted by user."
    exit 1
  fi
}

ensure_tag_available() {
  if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Tag $TAG already exists locally"; exit 1
  fi
  if git ls-remote --tags "$REMOTE" "refs/tags/${TAG}" | grep -q "$TAG"; then
    echo "Tag $TAG already exists on $REMOTE"; exit 1
  fi
}

setup_venv_build() {
  python3 -m venv .venv
  # shellcheck source=/dev/null
  source .venv/bin/activate
  pip install -U pip build twine
  rm -rf dist
  python -m build
  twine check dist/*
}

compose_release_notes() {
  local tmp
  tmp="$(mktemp -t gitspaces-release-XXXXXX.md)"
  if [[ "$MODE" == "editor" ]]; then
    local editor_cmd="${EDITOR:-nano}"
    printf "# %s\n\n" "$TAG" > "$tmp"
    printf "## Changes\n\n- " >> "$tmp"
    "$editor_cmd" "$tmp"
    RELEASE_NOTES="$(cat "$tmp")"
  elif [[ "$MODE" == "stdin" ]]; then
    echo "Paste release notes for $TAG (Ctrl-D to finish):"
    cat > "$tmp"
    RELEASE_NOTES="$(cat "$tmp")"
  else
    echo "Unknown compose mode: $MODE" >&2
    rm -f "$tmp"
    exit 1
  fi
  rm -f "$tmp"
  [[ -n "${RELEASE_NOTES// }" ]] || { echo "Empty release notes"; exit 1; }
}

create_and_push_tag() {
  git tag -a "$TAG" -m "$RELEASE_NOTES"
  if $PUSH; then
    git push "$REMOTE" "$TAG"
    echo "Pushed tag $TAG to $REMOTE"
  else
    echo "Tag $TAG created locally. Re-run with --push to push."
  fi
}

main() {
  parse_args "$@"
  check_branch_clean
  determine_tag
  confirm_tag
  ensure_tag_available
  setup_venv_build
  compose_release_notes
  create_and_push_tag
  echo "Release script completed for $TAG"
}

main "$@"