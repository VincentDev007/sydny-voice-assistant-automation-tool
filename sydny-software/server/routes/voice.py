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
    # save uploaded audio to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        # trip 1 — transcribe + reason
        transcript = transcribe_audio(tmp_path)
        result = await reason(transcript, db)
    finally:
        os.unlink(tmp_path)

    # if dangerous action — send back for confirmation
    if result.get("needs_confirm"):
        return {
            "needs_confirm": True,
            "intent": result["intent"],
            "target": result.get("target"),
            "response": result["response"]
        }

    # trip 2 — execute the action
    if result.get("intent"):
        execute_intent(result["intent"], result.get("target"))

    # trip 3 — speak
    speak(result["response"])

    return {"status": "ok", "end_session": result.get("end_session", False)}


@router.post("/confirm")
async def confirm_command(intent: str, target: str = None):
    # trip 2 — user confirmed, execute
    execute_intent(intent, target)

    # trip 3 — speak
    speak("Done.")

    return {"status": "ok"}
