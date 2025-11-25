#!/bin/bash
# setup-deadsnakes.sh
# Idempotently adds the deadsnakes PPA for Python versions on Ubuntu
set -euxo pipefail

# Because: Check if deadsnakes PPA is already configured
DEADSNAKES_REPO="ppa:deadsnakes/ppa"
DEADSNAKES_LIST="/etc/apt/sources.list.d/deadsnakes-ubuntu-ppa-*.list"

if ls $DEADSNAKES_LIST 1>/dev/null 2>&1; then
    echo "deadsnakes PPA already configured, skipping add-apt-repository"
else
    echo "Adding deadsnakes PPA..."
    sudo add-apt-repository -y "$DEADSNAKES_REPO"
fi

# Because: Always update apt cache after potential PPA addition
sudo apt-get update -qq

# Afterward: deadsnakes PPA is available for python version installs
echo "deadsnakes PPA setup complete"
