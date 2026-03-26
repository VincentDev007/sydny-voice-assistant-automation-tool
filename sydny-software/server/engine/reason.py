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

    raw = response.json()["message"]["content"]

    save_turn(db, role="user", content=transcript)
    save_turn(db, role="assistant", content=raw)

    return json.loads(raw)
