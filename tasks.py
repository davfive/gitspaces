"""Invoke tasks for gitspaces development."""

import sys
import json
import os
from pathlib import Path
from invoke import task, Exit

PROJECT_ROOT = Path(__file__).parent
PYVERSIONS_FILE = PROJECT_ROOT / ".python-versions.json"

def get_python_versions():
    """Get list of supported Python versions from .python-versions.json"""
    with open(PYVERSIONS_FILE) as f:
        return json.load(f)["python"]

def install_deps(c, python_version=None):
    """
    Sync dependencies using uv and return the environment dict.
    On Windows, we use version-specific suffixes to avoid file-locking issues.
    """
    is_windows = sys.platform == "win32"
    v = python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
    
    # Determine venv path: version-suffixed on Windows, standard on Unix/WSL
    venv = f".venv-{v}" if is_windows else ".venv"
    
    env = {"UV_PROJECT_ENVIRONMENT": venv}
    
    # On Windows, explicitly pass the python version to ensure the suffixed venv
    # is created with the correct interpreter.
    py_arg = f"--python {v}" if is_windows else ""
    
    c.run(f"uv sync --all-groups {py_arg}", warn=True, env=env)
    return env

# ============================================================================
# CI GATE TASKS
# ============================================================================

@task
def static(c):
    """Run static analysis (Ruff, Mypy)."""
    env = install_deps(c)
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    print(f"[static] Running analysis on Python {py_ver}...")
    c.run("uv run ruff format --check src/gitspaces tests", env=env)
    c.run("uv run ruff check src/gitspaces tests", env=env)
    c.run("uv run mypy src/gitspaces", env=env)

@task
def security(c, full=False):
    """Run security scans."""
    env = install_deps(c)
    
    print("[security] Running Bandit (Source Scan)...")
    report_args = "-f json -o bandit-report.json" if full else ""
    c.run(f"uv run bandit -r src/gitspaces {report_args}", env=env)
    
    if full:
        print("[security] Running Safety (Dependency Scan)...")
        c.run("uv run safety check --output text > safety-report.txt", warn=True, env=env)

# ============================================================================
# TESTING TASKS
# ============================================================================

@task
def test(c, python=None, args="", coverage=True):
    """Run tests for the current uv environment."""
    py_ver = python or f"{sys.version_info.major}.{sys.version_info.minor}"
    env = install_deps(c, python_version=py_ver)
    
    if coverage:
        env["COVERAGE_FILE"] = f".coverage.{py_ver}"
    
    cov_args = "--cov=src/gitspaces --cov-append" if coverage else ""
    
    print(f"[test] Running pytest on Python {py_ver}...")
    use_pty = sys.platform != "win32"
    result = c.run(f"uv run pytest -n auto {cov_args} {args}", warn=True, pty=use_pty, env=env)
    
    if result.exited != 0:
        raise Exit(f"Tests failed on {py_ver}", code=result.exited)

@task
def test_all(c):
    """Run full test matrix locally."""
    versions = get_python_versions()
    results = {}

    for v in versions:
        print(f"\n{'='*70}\nRunning: Python {v}\n{'='*70}")
        try:
            test(c, python=v)
            results[v] = True
        except Exit:
            results[v] = False

    print(f"\n{'='*70}\nCOMBINED COVERAGE REPORT\n{'='*70}")
    # Setup env for the first version to run coverage tools
    v_first = versions[0]
    is_win = sys.platform == "win32"
    combine_env = {"UV_PROJECT_ENVIRONMENT": f".venv-{v_first}" if is_win else ".venv"}
    
    c.run("uv run coverage combine", warn=True, env=combine_env)
    c.run("uv run coverage report", env=combine_env)
    
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
        ".coverage*", "coverage.xml", "bandit-report.json", "safety-report.txt",
        ".venv*" 
    ]
    for p in patterns:
        c.run(f"rm -rf {p}", warn=True)
    print("[PASS] Cleanup complete.")