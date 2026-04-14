import os
import tempfile
import asyncio
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
            "intent": result.get("intent"),
            "target": result.get("target"),
            "response": result.get("response", "")
        }

    if result.get("intent"):
        try:
            execute_intent(result["intent"], result.get("target"))
        except Exception as e:
            print(f"[voice] execute_intent error: {e}")

    response_text = result.get("response", "")
    if response_text:
        asyncio.create_task(asyncio.to_thread(speak, response_text))

    return {"status": "ok", "end_session": result.get("end_session", False)}


@router.post("/confirm")
async def confirm_command(intent: str, target: str = None):
    execute_intent(intent, target)
    asyncio.create_task(asyncio.to_thread(speak, "Done."))
    return {"status": "ok"}
