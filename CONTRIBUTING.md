# Contributing to GitSpaces

## Getting Started

1. Fork and clone the repository
2. Create a branch for your changes
3. Make changes and add tests
4. Submit a pull request

## Development Setup

### Install UV (one-time setup)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies
```bash
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
uv pip install -e .[dev]
```

## Development Workflow

### Running Tests
```bash
uv run invoke test              # Current Python version
uv run invoke test --python=3.14  # Specific version
uv run invoke test-all          # All versions (3.9-3.14)
```

### Code Quality
```bash
uv run invoke static            # All checks (ruff + mypy)
uv run invoke security          # Quick security scan (bandit)
uv run invoke security --full   # Deep scan (bandit + safety)

# Individual tools (if needed)
uv run ruff format src/gitspaces tests              # Auto-format
uv run ruff format --check src/gitspaces tests      # Check only
uv run ruff check src/gitspaces tests               # Lint
uv run ruff check --fix src/gitspaces tests         # Auto-fix
uv run mypy src/gitspaces                           # Type check
uv run bandit -r src/gitspaces                      # Security scan
uv run vulture src/gitspaces                        # Dead code
uv run xenon src/gitspaces                          # Complexity
```

### Full CI Pipeline Locally
```bash
uv run invoke ci-local          # static → security → test
```

### List All Tasks
```bash
uv run invoke --list
```

## Before Submitting PR

```bash
# Run full checks
uv run invoke ci-local

# Format code
uv run ruff format src/gitspaces tests
```

## Style Guide

- **Formatting**: Use `ruff format` (replaces black)
- **Line length**: 100 characters
- **Type hints**: Use where appropriate
- **Docstrings**: Google-style

## Commit Format

- Present tense, imperative mood
- First line ≤72 characters
- Reference issues/PRs

Example:
```
Add extend command for creating additional clones

- Implement cmd_extend module
- Add -n flag for clone count

Fixes #123
```

## Release Process

See [README.DEPLOYMENT.md](README.DEPLOYMENT.md) for deployment details.

Quick version:
1. Update version in `pyproject.toml` and `src/gitspaces/__init__.py`
2. Tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
3. Push: `git push origin v1.0.0`
4. GitHub Actions handles build and PyPI publish
