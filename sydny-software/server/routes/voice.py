import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from database import get_db
from engine.reason import reason
from services.voice_service import transcribe_audio, speak
from services.system_control import execute_intent

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/command")
async def voice_command(audio: UploadFile = File(...), db: Session = Depends(get_db)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        transcript = transcribe_audio(tmp_path)
        result = await reason(transcript, db)
    finally:
        os.unlink(tmp_path)

    if result.get("needs_confirm"):
        return {
            "needs_confirm": True,
            "intent": result["intent"],
            "target": result.get("target"),
            "response": result["response"]
        }

    speak(result["response"])

    return {"status": "ok", "end_session": result.get("end_session", False)}


@router.post("/confirm")
async def confirm_command(intent: str, target: str = None):
    execute_intent(intent, target)
    speak("Done.")
    return {"status": "ok"}
