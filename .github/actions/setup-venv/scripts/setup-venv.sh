#!/bin/bash
# setup-venv.sh
# Cross-platform bash script for creating and configuring a Python virtual environment
set -euxo pipefail

VENV_PATH="${1:-.venv}"
REQUIREMENTS_FILE="${2:-}"

# Because: Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
else
    echo "Virtual environment already exists at $VENV_PATH"
fi

# Because: Activate and upgrade pip
source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip

# Because: Install the package in editable mode (required for tests to import it)
python -m pip install -e .

# Because: Install requirements if file is specified and exists
if [ -n "$REQUIREMENTS_FILE" ] && [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    python -m pip install -r "$REQUIREMENTS_FILE"
fi

# Afterward: Virtual environment is ready for use
echo "Virtual environment setup complete at $VENV_PATH"
