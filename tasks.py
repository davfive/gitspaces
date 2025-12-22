"""Invoke tasks for gitspaces development.

Usage:
    uv run invoke test              # Test current Python version
    uv run invoke test-all          # Test all supported versions
    uv run invoke static            # Ruff + mypy checks
    uv run invoke security          # Security scans (--full for deep scan)
    uv run invoke ci-local          # Full CI pipeline

Individual tools (no invoke needed):
    uv run ruff format src/gitspaces tests
    uv run ruff check src/gitspaces tests
    uv run mypy src/gitspaces
    uv run bandit -r src/gitspaces
    uv run vulture src/gitspaces
    uv run xenon src/gitspaces
"""

import sys
import json
from pathlib import Path
from invoke import task, Exit

PROJECT_ROOT = Path(__file__).parent
PYVERSIONS_FILE = PROJECT_ROOT / ".python-versions.json"

def load_config():
    """Load configuration from .python-versions.json"""
    with open(PYVERSIONS_FILE) as f:
        return json.load(f)

def get_python_versions():
    """Get list of supported Python versions"""
    config = load_config()
    return config["python"]

# ============================================================================
# ORCHESTRATION TASKS
# ============================================================================

@task
def test(c, python=None, args="", coverage=True):
    """Run tests for current or specified Python version.
    
    Examples:
        uv run invoke test
        uv run invoke test --python=3.14
        uv run invoke test --args="tests/test_cli.py -k test_clone"
    """
    py_version = python or f"{sys.version_info.major}.{sys.version_info.minor}"
    
    cov_args = ""
    if coverage:
        cov_file = f"coverage-{py_version}.xml"
        cov_args = f"--cov=src/gitspaces --cov-report=xml:{cov_file} --cov-report=term-missing"
    
    cmd = f"pytest -n auto {cov_args} {args}"
    print(f"[test] Running tests with Python {py_version}...")
    
    result = c.run(cmd, warn=True, pty=True)
    if result.exited != 0:
        raise Exit(f"Tests failed for Python {py_version}", code=result.exited)


@task
def test_all(c, skip_versions=""):
    """Run tests across all supported Python versions.
    
    Reads versions from .python-versions.json
    
    Args:
        skip_versions: Comma-separated versions to skip (e.g., '3.9,3.10')
    
    Examples:
        uv run invoke test-all
        uv run invoke test-all --skip-versions=3.9,3.10
    """
    versions = get_python_versions()
    
    skip = [v.strip() for v in skip_versions.split(",") if v.strip()]
    versions_to_test = [v for v in versions if v not in skip]
    
    print(f"[test-all] Testing Python versions: {', '.join(versions_to_test)}")
    print(f"[test-all] (from {PYVERSIONS_FILE})")
    if skip:
        print(f"[test-all] Skipping: {', '.join(skip)}")
    
    results = {}
    for version in versions_to_test:
        print(f"\n{'='*70}")
        print(f"Testing Python {version}")
        print(f"{'='*70}\n")
        
        result = c.run(
            f"uv run --python {version} invoke test --python={version}",
            warn=True,
            pty=True
        )
        results[version] = result.exited == 0
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    
    for version, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  Python {version}: {status}")
    
    if not all(results.values()):
        failed = [v for v, passed in results.items() if not passed]
        raise Exit(f"Tests failed for: {', '.join(failed)}", code=1)
    
    print(f"\n✅ All {len(results)} Python versions passed!")


@task
def static(c):
    """Run all static analysis checks (ruff format, ruff check, mypy).
    
    Examples:
        uv run invoke static
    """
    print("[static] Running static analysis checks...\n")
    
    checks = [
        ("Ruff format check", "ruff format --check src/gitspaces tests"),
        ("Ruff lint check", "ruff check src/gitspaces tests"),
        ("Mypy type check", "mypy src/gitspaces"),
    ]
    
    failed = []
    for name, cmd in checks:
        print(f"{'='*70}")
        print(f"Running: {name}")
        print(f"{'='*70}")
        result = c.run(cmd, warn=True, pty=True)
        if result.exited != 0:
            failed.append(name)
        print()
    
    if failed:
        print(f"\n❌ Static analysis failed: {', '.join(failed)}")
        raise Exit(code=1)
    
    print("✅ All static analysis checks passed!")


@task
def security(c, full=False):
    """Run security scans.
    
    Args:
        full: Run full scan including dependency checks (default: False)
    
    Light mode (default):
        - bandit: Source code security scan
    
    Full mode (--full):
        - bandit: Source code security scan
        - safety: Known vulnerability database check
    
    Examples:
        uv run invoke security           # Quick scan (bandit only)
        uv run invoke security --full    # Deep scan (bandit + safety)
    """
    print(f"[security] Running {'FULL' if full else 'LIGHT'} security scan...\n")
    
    # Always run bandit
    print("="*70)
    print("Bandit: Source code security analysis")
    print("="*70)
    result = c.run("bandit -r src/gitspaces", warn=True, pty=True)
    bandit_passed = result.exited == 0
    print()
    
    safety_passed = True
    if full:
        print("="*70)
        print("Safety: Dependency vulnerability scan")
        print("="*70)
        result = c.run("safety check", warn=True, pty=True)
        safety_passed = result.exited == 0
        print()
    
    if not (bandit_passed and safety_passed):
        print("❌ Security scan failed!")
        raise Exit(code=1)
    
    print(f"✅ Security scan passed ({'full' if full else 'light'} mode)")


@task(pre=[static, security])
def ci_local(c, python=None):
    """Run full CI pipeline locally: static → security → test.
    
    Examples:
        uv run invoke ci-local              # Current Python version
        uv run invoke ci-local --python=3.14
    """
    print("\n" + "="*70)
    print("Running tests...")
    print("="*70 + "\n")
    test(c, python=python)
    
    print("\n" + "="*70)
    print("✅ LOCAL CI PIPELINE PASSED!")
    print("="*70)


@task
def clean(c):
    """Remove build artifacts, cache files, and coverage reports."""
    patterns = [
        "build/", "dist/", "*.egg-info", "**/__pycache__", "**/*.pyc",
        "**/*.pyo", ".pytest_cache", ".ruff_cache", ".mypy_cache",
        "htmlcov/", "coverage*.xml", ".coverage",
    ]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("✅ Cleaned build artifacts and cache files")
