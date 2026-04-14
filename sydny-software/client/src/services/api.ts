const API_URL = "http://localhost:8000";

export async function sendVoiceCommand(blob: Blob) {
  const formData = new FormData();
  formData.append("audio", blob, "audio.wav");
  const res = await fetch(`${API_URL}/api/voice/command`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`voice/command failed: ${res.status}`);
  return res.json();
}

export async function confirmCommand(intent: string, target: string | null) {
  const params = new URLSearchParams({ intent });
  if (target) params.append("target", target);
  const res = await fetch(`${API_URL}/api/voice/confirm?${params}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`voice/confirm failed: ${res.status}`);
  return res.json();
}
