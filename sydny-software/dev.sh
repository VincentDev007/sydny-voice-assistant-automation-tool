#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[SYDNY] Starting backend on localhost:8000..."

cd "$SCRIPT_DIR/server"
source venv/bin/activate

uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!  # save PID so we can kill it on exit

sleep 2

echo "[SYDNY] Starting Tauri desktop app..."

cd "$SCRIPT_DIR/client"
npm run tauri dev

echo "[SYDNY] Shutting down backend..."
kill $BACKEND_PID 2>/dev/null
echo "[SYDNY] Done."
