# Contributing to GitSpaces

Thank you for your interest in contributing to GitSpaces! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Push your changes to your fork
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/davfive/gitspaces.git
cd gitspaces
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install the package in editable mode:
```bash
pip install -e .
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if relevant**
- **Include your environment details** (OS, Python version, GitSpaces version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any similar features in other tools**

### Your First Code Contribution

Unsure where to begin? You can start by looking through these issues:

- Issues labeled `good first issue` - these should only require a few lines of code
- Issues labeled `help wanted` - these are issues that need attention

### Pull Requests

1. Ensure any install or build dependencies are removed before the end of the layer
2. Update the README.md with details of changes to the interface
3. Update the documentation with any new features or changes
4. Add tests for any new functionality
5. Ensure the test suite passes
6. Make sure your code lints (black, flake8)
7. Update the changelog if applicable

## Style Guidelines

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line Length**: Maximum 100 characters (not 79)
- **Formatting**: We use `black` for code formatting
- **Linting**: We use `flake8` for linting
- **Type Hints**: Use type hints where appropriate
- **Docstrings**: Use Google-style docstrings

### Running Linters and Security Checks

```bash
# Format code with black
black src/gitspaces tests

# Lint with flake8
flake8 src/gitspaces tests

# Type checking with mypy
mypy src/gitspaces

# Security scan with bandit
bandit -r src/gitspaces

# Check dependencies for vulnerabilities
safety check
```

### Testing

We use pytest for testing. Please write tests for any new functionality:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/gitspaces --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_config_singleton
```

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider starting the commit message with an applicable emoji:
  - 🎨 `:art:` when improving the format/structure of the code
  - 🐎 `:racehorse:` when improving performance
  - 📝 `:memo:` when writing docs
  - 🐛 `:bug:` when fixing a bug
  - 🔥 `:fire:` when removing code or files
  - ✅ `:white_check_mark:` when adding tests
  - 🔒 `:lock:` when dealing with security
  - ⬆️ `:arrow_up:` when upgrading dependencies
  - ⬇️ `:arrow_down:` when downgrading dependencies

Example:
```
✨ Add extend command to create additional clones

- Implement cmd_extend module
- Add -n flag for number of clones
- Update CLI to register extend command
- Add tests for extend functionality

Fixes #123
```

## Pull Request Process

1. **Update Documentation**: Ensure the README.md and any other relevant documentation are updated
2. **Add Tests**: Add tests that cover your changes
3. **Run Tests**: Ensure all tests pass locally
4. **Lint Your Code**: Run black and flake8 before submitting
5. **Update Changelog**: Add a note about your changes (if applicable)
6. **One Feature Per PR**: Keep pull requests focused on a single feature or bug fix
7. **Describe Your Changes**: Provide a clear description of what your PR does

### PR Review Process

1. At least one maintainer must approve the PR
2. All tests must pass
3. All review comments must be addressed
4. The branch must be up to date with main

## Development Workflow

### Branch Naming

- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation changes
- `refactor/description` - for code refactoring

### Release Process

For detailed deployment instructions, see [README.DEPLOYMENT.md](README.DEPLOYMENT.md).

Quick version:
1. Update version in `pyproject.toml` and `src/gitspaces/__init__.py`
2. Update CHANGELOG.md
3. Create a git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push the tag: `git push origin v1.0.0`
5. GitHub Actions will automatically build and publish to PyPI

## Project Structure

```
gitspaces/
├── src/gitspaces/         # Main package source
│   ├── modules/           # Core modules
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py            # CLI entry point
├── tests/                # Test files
├── docs/                 # Documentation
├── .github/              # GitHub workflows
├── pyproject.toml        # Package configuration
└── README.md
```

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to GitSpaces! 🚀
