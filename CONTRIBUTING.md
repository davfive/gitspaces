# Contributing to GitSpaces

## Getting Started

1. Fork and clone the repository
2. Create a branch for your changes
3. Make changes and add tests
4. Submit a pull request

## Development Setup

Requirements: Python 3.8+, Git

```bash
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

## Pull Request Guidelines

- Update README.md for interface changes
- Add tests for new functionality
- Ensure tests pass: `pytest`
- Format code: `black src/gitspaces tests`
- Lint: `flake8 src/gitspaces tests`
- Security scan: `bandit -r src/gitspaces`

## Style

- PEP 8, max line length 100
- Use `black` for formatting
- Use type hints where appropriate
- Google-style docstrings

## Testing

```bash
pytest                                    # run all tests
pytest --cov=src/gitspaces               # with coverage
pytest tests/test_config.py              # specific file
pytest tests/test_config.py::test_name   # specific test
```

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
