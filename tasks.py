"""Invoke tasks for gitspaces development."""

import sys
import json
from pathlib import Path
from invoke import task, Exit

PROJECT_ROOT = Path(__file__).parent
PYVERSIONS_FILE = PROJECT_ROOT / ".python-versions.json"

def get_python_versions():
    """Get list of supported Python versions from .python-versions.json"""
    with open(PYVERSIONS_FILE) as f:
        return json.load(f)["python"]

def install_deps(c):
    """Sync dependencies using uv."""
    # uv sync ensures the environment matches the lockfile exactly
    c.run("uv sync --extra dev", warn=True)

# ============================================================================
# CI GATE TASKS (Run once in CI on latest Ubuntu)
# ============================================================================

@task
def static(c):
    """Run static analysis (Ruff, Mypy)."""
    install_deps(c)
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"[static] Running analysis on Python {py_ver}...")
    
    c.run("uv run ruff format --check src/gitspaces tests")
    c.run("uv run ruff check src/gitspaces tests")
    c.run("uv run mypy src/gitspaces")

@task
def security(c, full=False):
    """Run security scans. Use --full in CI for deep dependency checks."""
    install_deps(c)
    print("[security] Running Bandit (Source Scan)...")
    # Generate a report file if we're in 'full' mode for CI upload
    report_args = "-f json -o bandit-report.json" if full else ""
    c.run(f"uv run bandit -r src/gitspaces {report_args}")
    
    if full:
        print("[security] Running Safety (Dependency Scan)...")
        # Safety report saved to text for easy CI artifact upload
        c.run("uv run safety check --output text > safety-report.txt", warn=True)

# ============================================================================
# TESTING TASKS (The Matrix)
# ============================================================================

@task
def test(c, python=None, args="", coverage=True):
    """Run tests for the current uv environment."""
    install_deps(c)
    py_ver = python or f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Isolate coverage files: .coverage.3.9, .coverage.3.10, etc.
    env = {"COVERAGE_FILE": f".coverage.{py_ver}"} if coverage else {}
    cov_args = "--cov=src/gitspaces --cov-append" if coverage else ""
    
    print(f"[test] Running pytest on Python {py_ver}...")
    result = c.run(f"uv run pytest -n auto {cov_args} {args}", warn=True, pty=True, env=env)
    
    if result.exited != 0:
        raise Exit(f"Tests failed on {py_ver}", code=result.exited)

@task
def test_all(c):
    """Run full test matrix locally with automatic uv version switching."""
    versions = get_python_versions()
    results = {}

    for v in versions:
        print(f"\n{'='*70}\nSwitching to Python {v}\n{'='*70}")
        # uv run --python handles the auto-download and isolated venv
        res = c.run(f"uv run --python {v} invoke test --python={v}", warn=True)
        results[v] = res.exited == 0

    print(f"\n{'='*70}\nCOMBINED COVERAGE REPORT\n{'='*70}")
    c.run("uv run coverage combine", warn=True)
    c.run("uv run coverage report")
    
    if not all(results.values()):
        raise Exit("Test matrix failed.", code=1)

# ============================================================================
# PIPELINES & UTILS
# ============================================================================

@task(pre=[static, security])
def ci_local(c):
    """Local check: Static analysis then Tests on current Python."""
    test(c)

@task
def clean(c):
    """Clean all cache, coverage, and report files."""
    patterns = [
        ".pytest_cache", ".ruff_cache", ".mypy_cache", ".uv_cache", 
        ".coverage*", "coverage.xml", "bandit-report.json", "safety-report.txt"
    ]
    for p in patterns:
        c.run(f"rm -rf {p}", warn=True)
    print("[PASS] Cleanup complete.")