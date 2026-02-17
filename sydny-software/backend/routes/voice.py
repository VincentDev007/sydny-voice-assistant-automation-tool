"""
Voice Routes
Endpoints for voice transcription and command processing.
"""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import tempfile
import os
from services.voice_service import transcribe_audio, speak
from services.command_parser import parse_command

router = APIRouter()


class TextRequest(BaseModel):
    text: str


# ============================================================
# TRANSCRIBE
# ============================================================

@router.post("/voice/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Receive audio file, return transcript text."""
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        content = await file.read()
        temp.write(content)
        temp.close()

        transcript = transcribe_audio(temp.name)
        return {"transcript": transcript}
    finally:
        os.unlink(temp.name)


# ============================================================
# COMMAND
# ============================================================

@router.post("/voice/command")
async def process_command(request: TextRequest):
    """Receive text, parse it into a command."""
    result = parse_command(request.text)
    return {
        "text": request.text,
        "intent": result["intent"],
        "target": result["target"],
        "needs_confirm": result["needs_confirm"]
    }


# ============================================================
# TEXT (shortcut)
# ============================================================

@router.post("/voice/text")
async def text_input(request: TextRequest):
    """Receive typed text, parse and return command."""
    result = parse_command(request.text)
    return {
        "text": request.text,
        "intent": result["intent"],
        "target": result["target"],
        "needs_confirm": result["needs_confirm"]
    }


# ============================================================
# SPEAK (TTS)
# ============================================================

@router.post("/voice/speak")
async def speak_text(request: TextRequest):
    """Speak text out loud using native OS TTS."""
    speak(request.text)
    return {"status": "ok", "text": request.text}
