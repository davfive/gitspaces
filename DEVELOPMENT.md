# Development Setup

## Prerequisites

- [UV](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Git

## Setup

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# OR: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone and setup
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
uv pip install -e .[dev]
```

## Running Tests

```bash
# Test current Python version
uv run invoke test

# Test all supported versions (3.9-3.14)
uv run invoke test-all

# Test specific version
uv run invoke test --python=3.11

# Test specific file
uv run invoke test --args="tests/test_cli.py"

# Test without coverage
uv run invoke test --no-coverage
```

## Code Quality

```bash
# Run all static checks (ruff + mypy)
uv run invoke static

# Run security scans
uv run invoke security          # Light (bandit only)
uv run invoke security --full   # Full (bandit + safety)

# Individual tools
uv run ruff format src/gitspaces tests              # Format code
uv run ruff check src/gitspaces tests               # Lint
uv run mypy src/gitspaces                           # Type check
```

## Local CI Pipeline

Run the full CI pipeline locally before pushing:

```bash
uv run invoke ci-local
```

This runs: static analysis → security scan → tests

## Supported Python Versions

Versions are defined in `.python-versions.json`:
- Python 3.9, 3.10, 3.11, 3.12, 3.13, 3.14
- Platforms: Ubuntu, macOS, Windows (cmd, pwsh, wsl)

UV automatically downloads and manages these Python versions.

## Project Structure

```
gitspaces/
├── .python-versions.json   # Supported versions (single source of truth)
├── tasks.py                # Invoke task definitions
├── src/gitspaces/          # Main package
│   ├── modules/            # Core modules
│   └── cli.py              # CLI entry point
├── tests/                  # Test suite
├── pyproject.toml          # Package metadata + tool config
└── .github/workflows/      # CI/CD workflows
```

## Troubleshooting

**UV not found after installation:**
```bash
# Reload shell or add to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**Import errors when running tests:**
```bash
# Ensure editable install
uv pip install -e .[dev]
```

**Python version not available:**
```bash
# UV will automatically download it
uv run --python 3.14 python --version
```
