const API_URL = "http://localhost:8000/api";

// ============================================================
// HEALTH
// ============================================================

export async function checkHealth() {
  const res = await fetch(`${API_URL}/health`);
  return res.json();
}

// ============================================================
// TASKS
// ============================================================

export async function fetchTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  return res.json();
}

export async function createTask(description: string, priority: string = "normal") {
  const res = await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description, priority }),
  });
  return res.json();
}

export async function updateTask(taskId: number, data: { description?: string; priority?: string; completed?: boolean }) {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteTask(taskId: number) {
  const res = await fetch(`${API_URL}/tasks/${taskId}`, {
    method: "DELETE",
  });
  return res.json();
}

// ============================================================
// VOICE
// ============================================================

export async function transcribeAudio(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/voice/transcribe`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function sendCommand(text: string) {
  const res = await fetch(`${API_URL}/voice/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

export async function sendText(text: string) {
  const res = await fetch(`${API_URL}/voice/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

export async function speakText(text: string) {
  const res = await fetch(`${API_URL}/voice/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return res.json();
}

// ============================================================
// SYSTEM
// ============================================================

export async function setVolume(level: number) {
  const res = await fetch(`${API_URL}/system/volume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ level }),
  });
  return res.json();
}

export async function mute() {
  const res = await fetch(`${API_URL}/system/mute`, { method: "POST" });
  return res.json();
}

export async function unmute() {
  const res = await fetch(`${API_URL}/system/unmute`, { method: "POST" });
  return res.json();
}

export async function openApp(appName: string) {
  const res = await fetch(`${API_URL}/system/open-app`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_name: appName }),
  });
  return res.json();
}

export async function closeApp(appName: string) {
  const res = await fetch(`${API_URL}/system/close-app`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_name: appName }),
  });
  return res.json();
}

export async function shutdownSystem() {
  const res = await fetch(`${API_URL}/system/shutdown`, { method: "POST" });
  return res.json();
}

export async function restartSystem() {
  const res = await fetch(`${API_URL}/system/restart`, { method: "POST" });
  return res.json();
}

export async function sleepSystem() {
  const res = await fetch(`${API_URL}/system/sleep`, { method: "POST" });
  return res.json();
}

export async function searchFile(filename: string) {
  const res = await fetch(`${API_URL}/system/search-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename }),
  });
  return res.json();
}

export async function openFile(filepath: string) {
  const res = await fetch(`${API_URL}/system/open-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filepath }),
  });
  return res.json();
}

export async function deleteFile(filepath: string) {
  const res = await fetch(`${API_URL}/system/delete-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filepath }),
  });
  return res.json();
}
