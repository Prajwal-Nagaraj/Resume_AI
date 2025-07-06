#!/usr/bin/env bash
# setup_backend.sh
# Creates and activates a Python virtual environment and installs dependencies

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Create venv if it does not exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend environment ready. Activate with: source $(pwd)/venv/bin/activate"