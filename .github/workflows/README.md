## Development and CI/CD

This project uses uv (https://docs.astral.sh/uv/) for dependency management and Invoke (https://www.pyinvoke.org/) for task automation.

### Local Development Setup

1. Install uv:
   $ curl -LsSf https://astral.sh/uv/install.sh | sh

2. Initialize Environment:
   $ uv sync

3. Run Common Tasks:
   - uv run invoke test      # Run standard test suite
   - uv run invoke static    # Run Ruff (linting) and Mypy (types)
   - uv run invoke security  # Run Bandit and Safety audits
   - uv run invoke test-all  # Run full multi-version matrix

### CI/CD Architecture

Our GitHub Actions pipeline follows a "Gate and Matrix" pattern:

* Push / Tag Trigger
    * Phase 1: THE GATE (Fast Feedback)
        * Runs static analysis and security audits.
        * If these fail, the workflow stops to save resources.
    * Phase 2: THE MATRIX (Cross-Platform Validation)
        * Runs tests across Ubuntu, macOS, Windows, and WSL.
        * Validates Python versions 3.9 through 3.14.
    * Phase 3: BUILD AND RELEASE (v*.*.* Tags Only)
        * Build: Generates distribution artifacts via 'uv build'.
        * Approval: Pauses for manual sign-off in the GitHub 'pypi' environment.
        * Publish: Uploads to PyPI using Trusted Publishing (OIDC).

### WSL Optimization

For Windows performance, CI uses a native WSL environment. Code is mirrored 
to the Linux ext4 filesystem to bypass NTFS mount overhead, resulting in 
significantly faster I/O during test execution.



### Versioning

We follow the "Single Source of Truth" model. The project version is 
managed in pyproject.toml. At runtime, the version is accessed via 
importlib.metadata:

from importlib.metadata import version
__version__ = version("gitspaces")