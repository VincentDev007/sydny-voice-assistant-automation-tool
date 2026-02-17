#!/bin/bash

# Start Sydny — backend + Tauri desktop app in one command

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend in background
echo "[SYDNY] Starting backend on localhost:8000..."
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start Tauri desktop app (blocks until you close it)
echo "[SYDNY] Starting Tauri desktop app..."
cd "$SCRIPT_DIR/frontend"
npm run tauri dev

# When Tauri closes, kill the backend
echo "[SYDNY] Shutting down backend..."
kill $BACKEND_PID 2>/dev/null
echo "[SYDNY] Done."
