# Development Setup

## Local Development

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/davfive/gitspaces.git
   cd gitspaces
   ```

2. **Install in editable mode:**
   ```bash
   pip install -e .
   ```
   
   This installs the package in development mode, allowing you to make changes to the code and test them immediately.

3. **Install development dependencies:**
   ```bash
   pip install -e .[dev]
   ```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/gitspaces --cov-report=term-missing

# Run specific test file
pytest tests/test_project.py -v
```


### Code Quality & Autofix

```bash
# Check code style, lint, types, security
./scripts/ci/static-checks.sh

# Autofix all autofixable issues (ruff, black)
./scripts/ci/static-checks.sh --fix

# Security scan only (skip type/lint)
./scripts/ci/static-checks.sh --quick
```

On Windows, use `.cmd` or `.ps1` variants.

### Troubleshooting

**Import errors when running tests:**

If you see errors like:
```
ImportError: No module named 'gitspaces'
```

Make sure you've installed the package in editable mode:
```bash
pip install -e .
```

**Module not found after installation:**

If the module still can't be found, verify your Python path:
```bash
python -c "import sys; print('\n'.join(sys.path))"
pip show gitspaces
```

## Project Structure

```
gitspaces/
├── src/gitspaces/          # Main package
│   ├── modules/            # Core modules
│   │   ├── config.py       # Configuration management
│   │   ├── project.py      # Project management
│   │   ├── space.py        # Space management
│   │   ├── runshell.py     # External command wrapper
│   │   └── cmd_*.py        # CLI commands
│   ├── cli.py              # CLI entry point
│   └── __init__.py
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Package metadata
└── requirements*.txt       # Dependencies
```
