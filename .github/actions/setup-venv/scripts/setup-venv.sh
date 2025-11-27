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

# Because: Build and install the package as a wheel (faster and more representative of user installs)
# Afterward: the package wheel is installed and importable
echo "Building package wheel..."
python -m pip install build
python -m build --wheel
echo "Installing package wheel..."
python -m pip install dist/*.whl

# Because: Install requirements if file is specified and exists
# Afterward: all dev dependencies are installed (local wheels first with fallback to index)
if [ -n "$REQUIREMENTS_FILE" ] && [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    # Try local wheels first if wheels directory exists
    if [ -d "wheels" ]; then
        echo "Attempting install from local wheels cache..."
        if python -m pip install --no-index --find-links wheels/ -r "$REQUIREMENTS_FILE" 2>/dev/null; then
            echo "Successfully installed from local wheels"
        else
            echo "Local wheels incomplete, falling back to index..."
            python -m pip install -r "$REQUIREMENTS_FILE"
        fi
    else
        python -m pip install -r "$REQUIREMENTS_FILE"
    fi
fi

# Afterward: Virtual environment is ready for use
echo "Virtual environment setup complete at ${VENV_PATH}"

# Export the actual venv path for callers that need it
export VENV_PATH
