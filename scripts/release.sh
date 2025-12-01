#!/usr/bin/env bash
set -euxo pipefail


# Globals
REMOTE="origin"
MODE=""          # "", "editor", or "stdin" (defaults to "stdin" if unset)
EXPLICIT_TAG=""
RELEASE_BRANCH=""
PREPARE_ONLY=false

SEMVER_TAG_RE='^v([0-9]+)\.([0-9]+)\.([0-9]+)(-[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?$'


parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --remote) REMOTE="$2"; shift 2 ;;
      --editor) MODE="editor"; shift ;;
      --stdin) MODE="stdin"; shift ;;
      --tag) EXPLICIT_TAG="$2"; shift 2 ;;
      --prepare) PREPARE_ONLY=true; shift ;;
      --branch) RELEASE_BRANCH="$2"; shift 2 ;;
      *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
  done
  if [[ -z "$MODE" ]]; then
    MODE="stdin"
  fi
}


check_branch_clean() {
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD)"
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

update_pyproject_version() {
  # Strip leading 'v' from tag to get version
  local version="${TAG#v}"
  
  # Update version in pyproject.toml
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed
    sed -i '' "s/^version = \".*\"/version = \"${version}\"/" pyproject.toml
  else
    # Linux sed
    sed -i "s/^version = \".*\"/version = \"${version}\"/" pyproject.toml
  fi
  
  echo "Updated pyproject.toml version to ${version}"
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

commit_version_changes() {
  git add pyproject.toml
  # Use first line of release notes as commit subject
  local subject
  subject="$(echo "$RELEASE_NOTES" | head -n1)"
  
  # Create commit message with subject and full notes as body
  git commit -m "$subject" -m "$RELEASE_NOTES"
  echo "Committed version update with release notes"
}

create_and_push_tag() {
  # Tag points to the commit we just made
  git tag -a "$TAG" -m "$RELEASE_NOTES"
  if $PUSH; then
    git push "$REMOTE" main
    git push "$REMOTE" "$TAG"
    echo "Pushed commit and tag $TAG to $REMOTE"
  else
    echo "Tag $TAG created locally. Re-run with --push to push commit and tag."
  fi
}


main() {
  parse_args "$@"

  if $PREPARE_ONLY; then
    # Step 1: Prepare release branch
    check_branch_clean
    local base_branch="main"
    git fetch "$REMOTE" "$base_branch"
    git checkout "$base_branch"
    git pull "$REMOTE" "$base_branch"
    determine_tag
    confirm_tag
    ensure_tag_available
    # Create release branch
    if [[ -z "$RELEASE_BRANCH" ]]; then
      RELEASE_BRANCH="release/${TAG}"
    fi
    git checkout -b "$RELEASE_BRANCH"
    update_pyproject_version
    compose_release_notes
    commit_version_changes
    git push -u "$REMOTE" "$RELEASE_BRANCH"
    echo "\nRelease branch '$RELEASE_BRANCH' prepared and pushed."
    echo "Open a PR to 'main' for this branch. After merge, tag the merged commit on main with:"
    echo "  git checkout main && git pull && git tag -a $TAG -m \"$TAG\" && git push $REMOTE $TAG"
    echo "Release notes (for tag):\n$RELEASE_NOTES"
    exit 0
  else
    # Step 2: Tag merged commit on main
    check_branch_clean
    local branch="$(git rev-parse --abbrev-ref HEAD)"
    if [[ "$branch" != "main" ]]; then
      echo "You must be on 'main' to tag the release after PR merge." >&2
      exit 1
    fi
    determine_tag
    confirm_tag
    ensure_tag_available
    compose_release_notes
    git tag -a "$TAG" -m "$RELEASE_NOTES"
    git push "$REMOTE" "$TAG"
    echo "Tag $TAG pushed to $REMOTE. CI will now publish the release."
    exit 0
  fi
}

main "$@"