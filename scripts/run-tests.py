#!/usr/bin/env python3
"""
Cross-platform test orchestrator used by small shell wrappers.

Usage:
  python scripts/run-tests.py            # run default/pyenv-local python(s)
  python scripts/run-tests.py 3.13       # single version
  python scripts/run-tests.py 3.9,3.10   # CSV list

This script:
- Installs Python via pyenv/pyenv-win (expects pyenv/pyenv-win available on PATH)
- Creates a per-version venv (.venv-<ver>)
- Installs package + dev requirements
- Runs pytest with coverage -> coverage-<ver>.xml
- Exits non-zero if any run fails
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)


def run(cmd: List[str], check: bool = True, capture: bool = False):
    print(">>>", " ".join(shlex.quote(c) for c in cmd))
    result = subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        text=True,
    )
    return result


def normalize_versions(arg: str) -> List[str]:
    if not arg:
        return []
    return [v.strip() for v in arg.split(",") if v.strip()]


def ensure_pyenv_available():
    if shutil.which("pyenv"):
        return "unix"
    if shutil.which("pyenv-win") or shutil.which("pyenv"):
        return "win"
    return None


def install_python_pyenv(version: str):
    run(["pyenv", "install", "-s", version], check=False)


def set_pyenv_shell(version: str):
    run(["pyenv", "shell", version], check=False)


def which_python_pyenv() -> str:
    res = run(["pyenv", "which", "python"], check=False, capture=True)
    if res and getattr(res, "stdout", None):
        return res.stdout.strip().splitlines()[-1]
    return "python"


def create_venv(python_exe: str, venv_dir: Path):
    run([python_exe, "-m", "venv", str(venv_dir)])
    return venv_dir


def pip_install(python_exe: str, reqs: List[str]):
    run([python_exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    if reqs:
        run([python_exe, "-m", "pip", "install"] + reqs)


def run_pytest(python_exe: str, cov_file: str):
    cmd = [
        python_exe,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=src/gitspaces",
        f"--cov-report=xml:{cov_file}",
        "--cov-report=term",
    ]
    return run(cmd, check=False).returncode


def main(argv: List[str]):
    arg = argv[1] if len(argv) > 1 else ""
    versions = normalize_versions(arg)

    pyenv_kind = ensure_pyenv_available()

    if not versions:
        versions = ["current"]

    overall_failed = False

    for ver in versions:
        print(f"\n=== Running for python version: {ver} ===\n")
        if ver != "current" and pyenv_kind:
            install_python_pyenv(ver)
            set_pyenv_shell(ver)
            python_path = which_python_pyenv()
        elif ver == "current":
            python_path = shutil.which("python") or sys.executable
        else:
            python_path = shutil.which("python") or sys.executable

        print("Using python:", python_path)
        venv_dir = ROOT / f".venv-{ver}"
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
        create_venv(python_path, venv_dir)

        venv_python = str(venv_dir / ("Scripts" if os.name == "nt" else "bin") / "python")
        try:
            pip_install(venv_python, ["-e", ".", "-r", "requirements-dev.txt"])
        except subprocess.CalledProcessError:
            print(f"pip install failed for {ver}", file=sys.stderr)
            overall_failed = True
            continue

        cov_file = f"coverage-{ver}.xml"
        rc = run_pytest(venv_python, cov_file)
        if rc != 0:
            print(f"pytest failed for {ver} (rc={rc})", file=sys.stderr)
            overall_failed = True

    if overall_failed:
        print("One or more python-version runs failed.", file=sys.stderr)
        sys.exit(1)

    print("All runs passed.")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)