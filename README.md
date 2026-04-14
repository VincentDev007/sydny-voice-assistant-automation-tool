# Sydny

![version](https://img.shields.io/badge/version-0.5.0-blue)
![platform](https://img.shields.io/badge/platform-macOS-lightgrey?logo=apple)

A local-first voice assistant and automation tool built with Tauri.

> macOS only. Windows and Linux support is not planned for this release.

## Features
- Wake word detection
- Voice recognition with Whisper
- Natural language intent parsing via Ollama
- Memory and reasoning engine
- System control and automation
- Ember Orb visual interface
- Real-time voice status

## Download
Get the latest release [here](https://github.com/your-username/sydny/releases).

## Setup
1. Open the downloaded `.dmg` and drag Sydny to your Applications folder
2. Remove the macOS quarantine flag (required since the app is not notarized):
   ```
   xattr -cr /Applications/Sydny.app
   ```
3. Install [Ollama](https://ollama.com/download)
4. Download `sydny.Modelfile` from the release page, then create the model:
   ```
   ollama create sydny -f sydny.Modelfile
   ```
5. Launch Sydny from Applications

## Running from Source
1. Clone the repo
2. Set up the backend:
   ```
   cd sydny-software/server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```
   cd sydny-software/client
   npm install
   ```
4. Start Ollama (skip if Ollama.app is already running):
   ```
   ollama serve
   ```
5. Start the app:
   ```
   cd sydny-software
   ./dev.sh
   ```

## Tech Stack
- Tauri
- React
- TypeScript
- Python (FastAPI)
- SQLite
- Ollama
