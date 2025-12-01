pip-cache composite action

Usage

- name: Prepare pip cache
  uses: ./.github/actions/pip-cache
  with:
    python-version: ${{ inputs.python-version }}
    windows-shell: ${{ inputs.windows-shell }}
    deps-files: |
      **/pyproject.toml
      **/requirements*.txt

Description

This composite action restores platform-specific pip caches (`http` and `wheels`).
- `http` (downloads) is keyed by platform + deps hash and is reusable across Python versions.
- `wheels` is keyed by platform + python-version + deps hash to avoid ABI collisions.

For Windows WSL runs the action uses a shuttle cache in the repository workspace (`.wsl-pip-cache`) that is restored/saved from the host so WSL's internal `~/.cache/pip` can be populated.

Diagnostics: the action prints cache sizes and presence to logs to help verify effectiveness.

Notes

- The action assumes hosted GitHub runners and availability of `wsl` on Windows when `windows-shell` is `wsl`.
- Adjust keys or paths if you have custom pip cache locations or want different invalidation semantics.
