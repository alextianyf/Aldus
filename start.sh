#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Aldus..."

# Start backend in background
cd "$SCRIPT_DIR/backend"
# Windows venv uses Scripts/, Linux/macOS uses bin/
if [[ -f "venv/Scripts/python" ]]; then
  VENV_PYTHON="venv/Scripts/python"
elif [[ -f "venv/Scripts/python.exe" ]]; then
  VENV_PYTHON="venv/Scripts/python.exe"
else
  VENV_PYTHON="venv/bin/python"
fi
$VENV_PYTHON -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend..."
for i in {1..20}; do
  curl -s http://localhost:8000/health >/dev/null 2>&1 && break
  sleep 0.5
done

# Open Chrome
URL="http://localhost:5173"
if grep -qi microsoft /proc/version 2>/dev/null; then
  # WSL — launch Windows Chrome
  cmd.exe /c start chrome "$URL" 2>/dev/null
elif [[ "$OSTYPE" == "darwin"* ]]; then
  open -a "Google Chrome" "$URL" 2>/dev/null || open "$URL"
else
  google-chrome "$URL" 2>/dev/null || xdg-open "$URL"
fi

# Start frontend (stays in foreground — Ctrl+C stops everything)
cd "$SCRIPT_DIR/frontend"
npm run dev

# When frontend exits, kill backend
kill $BACKEND_PID 2>/dev/null
