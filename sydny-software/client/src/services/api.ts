const API_URL = "http://localhost:8000";

// POST audio file → transcribe + reason → returns intent JSON or confirmation data
export async function sendVoiceCommand(blob: Blob) {
  const formData = new FormData();
  formData.append("audio", blob, "audio.wav");
  const res = await fetch(`${API_URL}/api/voice/command`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

// POST confirm a dangerous action after user clicks YES
export async function confirmCommand(intent: string, target: string | null) {
  const params = new URLSearchParams({ intent });
  if (target) params.append("target", target);
  const res = await fetch(`${API_URL}/api/voice/confirm?${params}`, {
    method: "POST",
  });
  return res.json();
}
