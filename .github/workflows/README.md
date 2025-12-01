# CI/CD Workflows

## Overview

```
test-latest.yml ─→ static-checks.yml ─→ run-tests (5 platforms × 1 Python)
test-all.yml    ─→ static-checks.yml ─→ run-tests (5 platforms × 5 Pythons sequential)
publish-pypi.yml ─→ test-all.yml ─→ build-pypi.yml ─→ TestPyPI ─→ PyPI
```

## Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `test-latest.yml` | Push to main/dev branches | Fast feedback: Python 3.13 only across all platforms |
| `test-all.yml` | PRs to main, manual | Full matrix: Python 3.9–3.13 across all platforms |
| `static-checks.yml` | Called by test workflows | Linting (flake8, black, mypy) + security scans |
| `publish-pypi.yml` | Tag `v*.*.*` | Full test → build → TestPyPI → PyPI |
| `build-pypi.yml` | Called by publish | Build wheel/sdist artifacts |
| `issue-states.yml` | Project card events | Sync issue states with project board |

## Test Platforms

| Platform | Shell | Job/Step Name |
|----------|-------|---------------|
| `ubuntu-latest` | bash | `test-ubuntu-bash-py*` |
| `macos-latest` | bash | `test-macos-bash-py*` |
| `windows-latest` | cmd | `test-windows-cmd-py*` |
| `windows-latest` | pwsh | `test-windows-pwsh-py*` |
| `windows-latest` | wsl-bash | `test-windows-wsl-py*` |

### Naming Convention
- **Jobs**: `test-{platform}-{shell}-pylatest` or `test-{platform}-{shell}-pyall`
- **Steps**: `test-{platform}-{shell}-py{version}` (e.g., `test-ubuntu-bash-py3.13`)

## Key Design Decisions

### Sequential Python versions in test-all.yml
Python versions (3.9–3.13) run as **sequential steps**, not matrix entries. Runner startup overhead (~2 min) exceeds per-version test time (~30s–1m30s). One runner tests all versions.

### WSL uses ext4 filesystem
WSL tests copy workspace to `~/gitspaces` (native ext4) instead of `/mnt/...` (NTFS). This provides ~10x I/O performance improvement.

### Editable installs for coverage
Tests use `pip install -e .` (not wheel installs) so pytest-cov measures `src/gitspaces/` correctly. Wheel installs cause 0% coverage.

### pytest-xdist parallelization
All tests run with `-n auto` for parallel execution within each platform/version.

## Composite Actions

Located in `.github/actions/`:

| Action | Purpose |
|--------|---------|
| `run-tests` | Setup Python, create venv, run pytest with coverage |
| `setup-wsl` | Install WSL Ubuntu + deadsnakes PPA for Python versions |

## Environment Variables

```yaml
env:
  LATEST_PYTHON_VERSION: '3.13'  # Used across workflows
```

## Supported Python Versions

- 3.13 (latest)
- 3.12
- 3.11
- 3.10
- 3.9

Update `test-all.yml` steps and `LATEST_PYTHON_VERSION` when adding/removing versions.
