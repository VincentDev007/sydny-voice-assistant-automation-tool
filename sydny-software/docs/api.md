# SYDNY — API Contract

## Overview

All endpoints are prefixed with /api.
Server runs on http://127.0.0.1:8000 — localhost only, never exposed to network.
All request and response bodies are JSON unless noted.
All endpoints require the shared secret token in the header (when implemented).

```
Base URL:     http://127.0.0.1:8000
Content-Type: application/json
Auth header:  X-Sydny-Token: <token>  (to be implemented)
```

---

## Error Response Shape

All errors return this shape:

```json
{
  "detail": "description of what went wrong"
}
```

Common status codes:
```
400   bad request — missing or invalid input
401   unauthorized — missing or invalid token
422   validation error — wrong data type or shape
429   rate limit exceeded
500   server error — something crashed
503   service unavailable — Ollama or Whisper not ready
```

---

## Voice Endpoints

---

### POST /api/voice/transcribe

Convert an audio file to text using Whisper STT.

**Request**
```
Content-Type: multipart/form-data
Body:         file — WAV audio file, max 10MB
```

**Response 200**
```json
{
  "transcript": "open safari"
}
```

**Errors**
```
400   no file provided
400   file is not WAV format
413   file exceeds 10MB limit
500   Whisper transcription failed
```

**Notes**
```
file is written to a temp .wav file
temp file is always deleted in try/finally
Whisper model must be loaded at startup
uses faster-whisper for performance
```

---

### POST /api/voice/command

Send a transcript to the brain and get back a structured command plan.
This is the main brain endpoint — calls memory + Ollama internally.

**Request**
```json
{
  "text": "open safari"
}
```

**Response 200**
```json
{
  "response":      "Opening Safari.",
  "intent":        "open-app",
  "target":        "safari",
  "needs_confirm": false
}
```

**Response 200 — conversation (no skill)**
```json
{
  "response":      "What's left to finish? Let's figure it out.",
  "intent":        null,
  "target":        null,
  "needs_confirm": false
}
```

**Response 200 — dangerous command**
```json
{
  "response":      "Shut down?",
  "intent":        "shutdown",
  "target":        null,
  "needs_confirm": true
}
```

**Errors**
```
400   text field missing or empty
400   text exceeds 500 characters
503   Ollama not running or unreachable
500   brain returned invalid response
```

**Notes**
```
checks command cache before calling Ollama
loads last 6 memory turns from SQLite
saves user turn + sydny turn to SQLite after response
validates intent against whitelist before returning
enforces needs_confirm: true for shutdown/restart/sleep/delete-file
text is sanitized — control characters stripped
```

---

### POST /api/voice/text

Same as /api/voice/command but for typed keyboard input.
Identical behavior — separate endpoint for clarity.

**Request**
```json
{
  "text": "search for report.pdf"
}
```

**Response 200**
```json
{
  "response":      "Searching for report.pdf.",
  "intent":        "search-file",
  "target":        "report.pdf",
  "needs_confirm": false
}
```

**Errors**
```
same as /api/voice/command
```

---

### POST /api/voice/speak

Speak text out loud using macOS native TTS.
Called after every command execution with Sydny's response text.

**Request**
```json
{
  "text": "Opening Safari."
}
```

**Response 200**
```json
{
  "status": "ok",
  "text":   "Opening Safari."
}
```

**Errors**
```
400   text field missing or empty
400   text exceeds 500 characters
500   TTS command failed
```

**Notes**
```
blocking call — response returns only after speech finishes
text is sanitized before passing to macOS say
macOS only for now — Windows and Linux stubs exist
```

---

## System Endpoints

---

### POST /api/system/open-app

Open an application by name.

**Request**
```json
{
  "app_name": "safari"
}
```

**Response 200**
```json
{
  "message": "Opening safari."
}
```

**Errors**
```
400   app_name missing or empty
400   app_name exceeds 100 characters
500   failed to open application
```

**Notes**
```
runs: open -a <app_name>
app_name is validated — no shell special characters
no shell=True — args passed as list
```

---

### POST /api/system/close-app

Close an application by name.

**Request**
```json
{
  "app_name": "safari"
}
```

**Response 200**
```json
{
  "message": "Closing safari."
}
```

**Errors**
```
400   app_name missing or empty
400   app_name exceeds 100 characters
500   failed to close application
```

**Notes**
```
runs: osascript -e 'quit app "<app_name>"'
app_name validated before execution
```

---

### POST /api/system/volume

Set system volume to a specific level.

**Request**
```json
{
  "level": 50
}
```

**Response 200**
```json
{
  "message": "Volume set to 50."
}
```

**Errors**
```
400   level missing
400   level is not an integer
400   level is not between 0 and 100
500   failed to set volume
```

**Notes**
```
runs: osascript -e 'set volume output volume <level>'
level is validated as integer 0-100 before execution
```

---

### POST /api/system/mute

Mute system audio.

**Request**
```json
{}
```

**Response 200**
```json
{
  "message": "Muted."
}
```

**Errors**
```
500   failed to mute
```

---

### POST /api/system/unmute

Unmute system audio.

**Request**
```json
{}
```

**Response 200**
```json
{
  "message": "Unmuted."
}
```

**Errors**
```
500   failed to unmute
```

---

### POST /api/system/shutdown

Shut down the Mac.
Frontend only calls this after user confirms in the confirmation dialog.

**Request**
```json
{}
```

**Response 200**
```json
{
  "message": "Shutting down."
}
```

**Errors**
```
500   failed to initiate shutdown
```

**Notes**
```
runs: sudo shutdown -h now
requires confirmation dialog before frontend calls this
```

---

### POST /api/system/restart

Restart the Mac.
Frontend only calls this after user confirms in the confirmation dialog.

**Request**
```json
{}
```

**Response 200**
```json
{
  "message": "Restarting."
}
```

**Errors**
```
500   failed to initiate restart
```

---

### POST /api/system/sleep

Put the Mac to sleep.
Frontend only calls this after user confirms in the confirmation dialog.

**Request**
```json
{}
```

**Response 200**
```json
{
  "message": "Sleeping."
}
```

**Errors**
```
500   failed to initiate sleep
```

---

### POST /api/system/search-file

Search for a file by name across common directories.

**Request**
```json
{
  "filename": "report.pdf"
}
```

**Response 200 — found**
```json
{
  "message": "Found report.pdf.",
  "results": [
    "/Users/vincent/Documents/report.pdf",
    "/Users/vincent/Downloads/report.pdf"
  ]
}
```

**Response 200 — not found**
```json
{
  "message": "No files found matching report.pdf.",
  "results": []
}
```

**Errors**
```
400   filename missing or empty
400   filename exceeds 200 characters
500   search failed
```

**Notes**
```
searches: ~/Documents, ~/Downloads, ~/Desktop, ~/Desktop
filename validated — no shell special characters
results are absolute paths
```

---

### POST /api/system/open-file

Open a file with the default application.

**Request**
```json
{
  "filepath": "/Users/vincent/Documents/report.pdf"
}
```

**Response 200**
```json
{
  "message": "Opening report.pdf."
}
```

**Errors**
```
400   filepath missing or empty
400   filepath contains .. traversal
404   file does not exist
500   failed to open file
```

**Notes**
```
runs: open <filepath>
filepath is resolved to absolute path
.. traversal is rejected
file existence is verified before executing
```

---

### POST /api/system/delete-file

Permanently delete a file.
Frontend only calls this after user confirms in the confirmation dialog.

**Request**
```json
{
  "filepath": "/Users/vincent/Downloads/old-notes.txt"
}
```

**Response 200**
```json
{
  "message": "Deleted old-notes.txt."
}
```

**Errors**
```
400   filepath missing or empty
400   filepath contains .. traversal
400   filepath is a directory — only files allowed
404   file does not exist
500   failed to delete file
```

**Notes**
```
uses os.remove() — not shell command
filepath resolved to absolute path
.. traversal rejected
file existence verified before deleting
directory deletion not allowed — files only
this is irreversible — no recycle bin
```

---

## Platform Endpoint

---

### GET /api/platform

Returns information about the current operating system.
Called on frontend startup to detect platform.

**Request**
```
no body
```

**Response 200**
```json
{
  "platform":      "mac",
  "version":       "14.3.1",
  "architecture":  "arm64"
}
```

**Notes**
```
platform is one of: "mac", "windows", "linux"
used by frontend to show platform-specific UI if needed
```

---

## Health Endpoint

---

### GET /api/health

Check if the server is running and all dependencies are ready.

**Request**
```
no body
```

**Response 200 — all good**
```json
{
  "status":  "ok",
  "whisper": "ready",
  "ollama":  "ready",
  "db":      "ready"
}
```

**Response 200 — degraded**
```json
{
  "status":  "degraded",
  "whisper": "ready",
  "ollama":  "unreachable",
  "db":      "ready"
}
```

**Notes**
```
called by frontend on startup to verify backend is up
if ollama is unreachable — brain will not work
if whisper is not loaded — transcription will not work
frontend can show warning if status is degraded
```

---

## Rate Limits

```
POST /api/voice/transcribe    10 requests per minute
POST /api/voice/command       20 requests per minute
POST /api/voice/text          20 requests per minute
POST /api/voice/speak         20 requests per minute
POST /api/system/*            30 requests per minute
GET  /api/platform            no limit
GET  /api/health              no limit
```

---

## Request Size Limits

```
audio file upload    10MB max
JSON body            1MB max
text fields          500 chars max
app_name             100 chars max
filename             200 chars max
filepath             500 chars max
```

---

## Full Endpoint List

```
GET  /api/health
GET  /api/platform

POST /api/voice/transcribe
POST /api/voice/command
POST /api/voice/text
POST /api/voice/speak

POST /api/system/open-app
POST /api/system/close-app
POST /api/system/volume
POST /api/system/mute
POST /api/system/unmute
POST /api/system/shutdown
POST /api/system/restart
POST /api/system/sleep
POST /api/system/search-file
POST /api/system/open-file
POST /api/system/delete-file
```
