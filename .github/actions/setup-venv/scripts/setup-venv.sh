#!/usr/bin/env bash
# setup-venv.sh
# Cross-platform bash script for creating and configuring a Python virtual environment
# Supports CI matrix jobs by creating a separate venv per Python version
set -euxo pipefail

VENV_PATH_BASE="${1:-.venv}"
REQUIREMENTS_FILE="${2:-}"

# Because: ensure that when matrix jobs run multiple Python versions on the same runner, each Python version gets an isolated venv
# Afterward: a venv directory named .venv-py<M>.<m> exists and its python matches the current interpreter
PY_VER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
VENV_PATH="${VENV_PATH_BASE}-py${PY_VER}"

# Because: reuse a venv only when it already matches the interpreter version
# Afterward: existing venv is kept if it matches; otherwise it's removed so we recreate it
if [ -d "${VENV_PATH}" ]; then
    if [ -x "${VENV_PATH}/bin/python" ]; then
        EXISTING_VER="$(${VENV_PATH}/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
        if [ "${EXISTING_VER}" != "${PY_VER}" ]; then
            echo "Existing venv python ${EXISTING_VER} does not match current python ${PY_VER}; recreating ${VENV_PATH}"
            rm -rf "${VENV_PATH}"
        else
            echo "Using existing venv ${VENV_PATH} (python ${EXISTING_VER})"
        fi
    else
        echo "Venv dir exists but no python binary found; recreating ${VENV_PATH}"
        rm -rf "${VENV_PATH}"
    fi
fi

# Because: create a venv tied to the current python interpreter
# Afterward: ${VENV_PATH} exists and is activated
if [ ! -d "${VENV_PATH}" ]; then
    echo "Creating virtual environment at ${VENV_PATH}..."
    python3 -m venv "${VENV_PATH}"
fi

# Because: Activate and upgrade pip
source "${VENV_PATH}/bin/activate"
python -m pip install --upgrade pip

# Because: Install the package in editable mode (required for tests to import it)
python -m pip install -e .

# Because: Install requirements if file is specified and exists
if [ -n "$REQUIREMENTS_FILE" ] && [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    python -m pip install -r "$REQUIREMENTS_FILE"
fi

# Afterward: Virtual environment is ready for use
echo "Virtual environment setup complete at ${VENV_PATH}"

# Export the actual venv path for callers that need it
export VENV_PATH
