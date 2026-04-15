# Changelog

All notable changes to Sydny will be documented here.

## [Unreleased]

## [0.5.0] - 2026-04-13
### Added
- Engine layer with reasoning and memory system
- Ollama integration via Sydny Modelfile
- New voice routes for session-based voice handling
- Intent execution pipeline
- PyInstaller sidecar bundling Python backend into the Tauri app
- `run.py` as PyInstaller entry point with `freeze_support` for frozen binary compatibility
- `sydny-server.spec` PyInstaller spec bundling ffmpeg, CTranslate2, faster-whisper, and uvicorn
- Ollama auto-start on app launch via hardcoded Homebrew path
- Persistent SQLite database in `~/Library/Application Support/Sydny/`

### Changed
- Replaced HAL eye UI with Ember Orb and new session state system
- Rebuilt frontend state architecture
- Refactored backend into engine layer
- Renamed `backend_requirements.txt` to `requirements.txt`
- TTS (`say`) now runs on a background thread so the server never blocks mid-request
- Database path moved from relative `./sydny.db` to macOS Application Support directory

### Fixed
- Intent execution restoring full command flow
- CI requirements file path in build workflow
- Server freezing during TTS playback in packaged app (single-worker uvicorn blocked by `subprocess.run`)
- PyInstaller multiprocessing explosion causing hundreds of `[Errno 48]` port binding errors
- Ollama not auto-starting in packaged app due to missing shell PATH
- Backend sidecar crashing on startup due to read-only `.app` bundle directory blocking database writes
- Hardcoded Ollama Homebrew path replaced with dynamic PATH resolution
- Platform database detection failing on certain macOS configurations
- Legacy HAL eye color values leaking into Ember Orb styles
- PyInstaller sidecar using windowed bootloader (`runw`) causing macOS to kill the server process after ~10 seconds — switched to console bootloader (`run`)
- Ollama auto-start blocking Tauri `setup()` for up to 10 seconds before window appeared — moved to background thread
- KeyError crashes when Ollama returns unexpected response structure
- JSONDecodeError crash when Ollama returns non-JSON content
- `int(target)` ValueError in `execute_intent` when LLM returns non-numeric volume target
- `shutdown`, `restart`, and `sleep` returning success regardless of subprocess exit code
- `res.json()` called without checking `res.ok` in frontend API calls
- Unhandled intents in `execute_intent` now logged instead of silently ignored
- `load_context` using redundant `order_by(desc).reverse()` — replaced with `order_by(asc)`
- Removed unused `sessionActive` state and `StatusLabel` component

## [0.1.0] - 2026-03-22
### Added
- FastAPI backend with SQLite database
- Voice recognition and command parsing pipeline
- Task management with CRUD operations
- System control and platform abstraction layer
- Tauri + React frontend with HAL eye UI
- Real-time voice status and terminal output
- macOS support
