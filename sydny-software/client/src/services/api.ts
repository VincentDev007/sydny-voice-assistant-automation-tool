// ============================================================
// api.ts — Backend HTTP Client
// ============================================================
// A centralized module for ALL backend communication.
// Every HTTP call to the FastAPI backend goes through this file.
//
// WHY CENTRALIZE API CALLS HERE?
//   Single place to change the backend URL.
//   Easy to see all available endpoints.
//   Components and hooks import from here — they don't write fetch() calls themselves.
//   If an endpoint URL changes, we only update it in one place.
//
// HOW fetch() WORKS (brief):
//   fetch(url) → sends an HTTP GET request
//   fetch(url, { method: "POST", headers: {...}, body: JSON.stringify(data) }) → POST with JSON
//   .json() → parses the response body as JSON and returns it
//   All fetch() calls are async → must be awaited or chained with .then()
//
// PATTERN FOR ALL FUNCTIONS:
//   1. Build the URL from API_URL + endpoint path
//   2. Call fetch() with method, headers, and body
//   3. Parse and return the JSON response
//   The caller handles errors (try/catch in App.tsx and useVoice.ts)
// ============================================================

// Base URL for all API calls
// All backend endpoints live under this prefix
const API_URL = "http://localhost:8000/api";


// ============================================================
// HEALTH CHECK
// ============================================================

// Ping the backend to check if it's alive
// Used on startup to verify connectivity
export async function checkHealth() {
  const res = await fetch(`${API_URL}/health`); // GET /api/health
  return res.json();                             // Returns: { "status": "healthy" }
}


// ============================================================
// TASKS — CRUD operations
// ============================================================

// GET all tasks from the database
// Returns: Task[] (array of task objects)
export async function fetchTasks() {
  const res = await fetch(`${API_URL}/tasks`); // GET /api/tasks
  return res.json();
}

// POST create a new task
// priority defaults to "normal" if not specified
// Returns: the newly created Task with its database-assigned ID
export async function createTask(description: string, priority: string = "normal") {
  const res = await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }, // Tell the backend to expect JSON
    body: JSON.stringify({ description, priority }),  // Convert JS object to JSON string
  });
  return res.json();
}

// PUT update an existing task by ID
// `data` is partial — only include fields you want to change
// Example: updateTask(3, { completed: true })
// Returns: the updated Task object
export async function updateTask(taskId: number, data: { description?: string; priority?: string; completed?: boolean }) {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, { // PUT /api/tasks/3
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// DELETE remove a task permanently
// Returns: { "message": "Task 3 deleted" }
export async function deleteTask(taskId: number) {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, { // DELETE /api/tasks/3
    method: "DELETE",
  });
  return res.json();
}


// ============================================================
// VOICE — Transcription, Parsing, and TTS
// ============================================================

// POST audio file → transcribed text
// Uses FormData (multipart/form-data) instead of JSON because we're sending a file
// The backend saves it as a temp WAV file, runs Whisper, and returns the transcript
// Returns: { "transcript": "open safari" }
export async function transcribeAudio(file: File) {
  const formData = new FormData();
  formData.append("file", file);         // Attach the WAV file
  const res = await fetch(`${API_URL}/voice/transcribe`, {
    method: "POST",
    body: formData,                       // No Content-Type header needed — fetch sets it automatically for FormData
  });
  return res.json();
}

// POST text → parsed command (from voice input pipeline)
// Used by useVoice.ts after getting the transcript from transcribeAudio()
// Returns: { text, intent, target, needs_confirm }
export async function sendCommand(text: string) {
  const res = await fetch(`${API_URL}/voice/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

// POST text → parsed command (from typed input)
// Used by useStore.sendTextCommand() for keyboard input
// Identical behavior to sendCommand() — different endpoint for semantic clarity
// Returns: { text, intent, target, needs_confirm }
export async function sendText(text: string) {
  const res = await fetch(`${API_URL}/voice/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

// POST text → speak it out loud using native OS TTS
// On macOS: backend runs `say "text"` — blocking until speech completes
// Only used for SYDNY's responses, NOT for reading back the user's transcript
// Returns: { "status": "ok", "text": "..." }
export async function speakText(text: string) {
  const res = await fetch(`${API_URL}/voice/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}


// ============================================================
// SYSTEM — Computer control endpoints
// ============================================================

// POST set system volume to a level between 0 and 100
// On macOS: runs `osascript -e "set volume output volume 50"`
// Returns: { "message": "Volume set to 50" }
export async function setVolume(level: number) {
  const res = await fetch(`${API_URL}/system/volume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ level }),
  });
  return res.json();
}

// POST mute system audio — no body needed
// Returns: { "message": "System muted" }
export async function mute() {
  const res = await fetch(`${API_URL}/system/mute`, { method: "POST" });
  return res.json();
}

// POST unmute system audio — no body needed
// Returns: { "message": "System unmuted" }
export async function unmute() {
  const res = await fetch(`${API_URL}/system/unmute`, { method: "POST" });
  return res.json();
}

// POST open an application by name
// On macOS: runs `open -a appName`
// Note: app_name (snake_case) matches the Python Pydantic model field name
// Returns: { "message": "Opened safari" }
export async function openApp(appName: string) {
  const res = await fetch(`${API_URL}/system/open-app`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_name: appName }), // snake_case to match Python schema
  });
  return res.json();
}

// POST close an application by name
// On macOS: runs AppleScript `quit app "appName"`
// Returns: { "message": "Closed safari" }
export async function closeApp(appName: string) {
  const res = await fetch(`${API_URL}/system/close-app`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_name: appName }),
  });
  return res.json();
}

// POST shutdown the computer — no body needed — DANGEROUS
// Returns: { "message": "Shutting down" } (then the computer shuts down)
export async function shutdownSystem() {
  const res = await fetch(`${API_URL}/system/shutdown`, { method: "POST" });
  return res.json();
}

// POST restart the computer — no body needed — DANGEROUS
// Returns: { "message": "Restarting" }
export async function restartSystem() {
  const res = await fetch(`${API_URL}/system/restart`, { method: "POST" });
  return res.json();
}

// POST put the computer to sleep — no body needed
// Returns: { "message": "Going to sleep" }
export async function sleepSystem() {
  const res = await fetch(`${API_URL}/system/sleep`, { method: "POST" });
  return res.json();
}

// POST search for a file by name in common directories (Desktop, Documents, Downloads, Home)
// Returns up to 10 matching file paths
// Returns: { "matches": ["/Users/you/Desktop/report.pdf", ...] }
export async function searchFile(filename: string) {
  const res = await fetch(`${API_URL}/system/search-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });
  return res.json();
}

// POST open a file with its default application
// On macOS: runs `open filepath`
// Returns: { "message": "Opened /path/to/file.pdf" }
export async function openFile(filepath: string) {
  const res = await fetch(`${API_URL}/system/open-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filepath }),
  });
  return res.json();
}

// POST permanently delete a file — DANGEROUS, IRREVERSIBLE
// Only called after the user confirms in ConfirmDialog
// Returns: { "message": "Deleted /path/to/file.txt" }
export async function deleteFile(filepath: string) {
  const res = await fetch(`${API_URL}/system/delete-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filepath }),
  });
  return res.json();
}
