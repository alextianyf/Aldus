#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo " Aldus - First Time Setup"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  echo "[ERROR] Python not found. Please install Python from https://python.org"
  exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
  echo "[ERROR] Node.js not found. Please install Node.js from https://nodejs.org"
  exit 1
fi

PYTHON=$(command -v python3 || command -v python)

echo "[1/2] Setting up Python backend..."
cd "$SCRIPT_DIR/backend"
$PYTHON -m venv venv --system-site-packages
venv/bin/pip install -r requirements.txt

echo
echo "[2/2] Installing frontend dependencies..."
cd "$SCRIPT_DIR/frontend"
npm install

echo
echo "Done! Run ./start.sh to launch Aldus."
