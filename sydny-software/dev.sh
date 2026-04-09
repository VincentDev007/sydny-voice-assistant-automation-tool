#!/bin/bash

# ============================================================
# dev.sh — Single-Command SYDNY Startup Script (v0.5.0)
# ============================================================
# Starts both the backend (FastAPI) and frontend (Tauri + React) together.
# Before this script, you had to open two terminals and start them separately.
#
# HOW IT WORKS:
#   1. Detects the directory where this script lives (project root)
#   2. Starts the FastAPI backend in the BACKGROUND on port 8000
#   3. Waits 2 seconds for the backend to initialize
#   4. Starts the Tauri frontend in the FOREGROUND (blocks until you close the window)
#   5. When the Tauri window closes, kills the background backend process
#
# USAGE:
#   ./dev.sh
#   (run from the project root — or any directory, it finds itself)
#
# PREREQUISITES:
#   - Ollama is installed and running: `ollama serve` (separate terminal)
#   - Sydny model is pulled: `ollama create sydny -f server/engine/sydny.Modelfile`
#   - Python venv exists at server/venv/
#   - All pip packages installed (pip install -r server/requirements.txt)
#   - Node modules installed (npm install in client/)
#   - Rust/Cargo toolchain installed (for Tauri)
#
# WHY `&` after uvicorn?
#   The `&` runs the command in the background — the script continues immediately
#   to the next line instead of waiting for uvicorn to exit.
#   We store its PID ($!) so we can kill it when Tauri closes.
#
# WHY sleep 2?
#   uvicorn needs a moment to start FastAPI and load faster-whisper.
#   Without this delay, Tauri might try to connect before the backend is ready.
#
# WHY kill $BACKEND_PID at the end?
#   Without this, uvicorn would keep running in the background after you close
#   the Tauri window, using CPU and holding port 8000. The kill ensures cleanup.
# ============================================================


# Find the directory where this script is located (the project root)
# dirname "$0" → the directory of this script
# cd + pwd     → resolve to an absolute path (handles relative paths and symlinks)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"


# ── Start the FastAPI backend in the background ──
echo "[SYDNY] Starting backend on localhost:8000..."

# Navigate to the server directory
cd "$SCRIPT_DIR/server"

# Activate the Python virtual environment
# This makes `uvicorn` and all installed pip packages available
source venv/bin/activate

# Start uvicorn in the background (&)
# app:app → the `app` variable in the `app.py` file
# --reload → auto-restart when code changes (development mode)
# --port 8000 → listen on port 8000 (frontend connects to this)
uvicorn app:app --reload --port 8000 &

# Save the background process ID so we can kill it later
BACKEND_PID=$!


# ── Wait for the backend to finish starting ──
# The backend needs to: start uvicorn → load FastAPI → load faster-whisper model
# 2 seconds is usually enough; adjust if the backend is slow to start on your machine
sleep 2


# ── Start the Tauri frontend (blocks here until window is closed) ──
echo "[SYDNY] Starting Tauri desktop app..."

# Navigate to the client directory
cd "$SCRIPT_DIR/client"

# Run Tauri dev mode:
#   - Starts Vite dev server on localhost:1420 (serves React)
#   - Compiles Rust code and opens the native desktop window
#   - Hot-reloads when frontend code changes
# This command BLOCKS — the script waits here until the Tauri window is closed
npm run tauri dev


# ── Cleanup: kill the backend when Tauri closes ──
# When `npm run tauri dev` exits (window closed), execution resumes here
echo "[SYDNY] Shutting down backend..."

# Kill the uvicorn process by PID
# 2>/dev/null → suppress "No such process" error if it already died
kill $BACKEND_PID 2>/dev/null

echo "[SYDNY] Done."
