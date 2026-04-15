import httpx
import json
from sqlalchemy.orm import Session
from engine.memory import load_context, save_turn

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "sydny"

async def reason(transcript: str, db: Session) -> dict:
    context = load_context(db)

    messages = context + [{"role": "user", "content": transcript}]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": messages,
            "stream": False
        })

    try:
        raw = response.json()["message"]["content"]
    except (KeyError, ValueError) as e:
        print(f"[reason] unexpected Ollama response: {e}\n{response.text}")
        return {"response": "I had trouble processing that.", "intent": None}

    save_turn(db, role="user", content=transcript)
    save_turn(db, role="assistant", content=raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[reason] failed to parse Ollama JSON: {e}\nRaw: {raw}")
        return {"response": raw, "intent": None}
