#!/usr/bin/env bash
# setup_frontend.sh
# Installs Node dependencies for the frontend project

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

if [ ! -f package.json ]; then
  echo "Error: package.json not found in $(pwd)" >&2
  exit 1
fi

npm install

echo "✅ Frontend dependencies installed."