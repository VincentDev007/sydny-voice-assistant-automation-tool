"""
Voice Routes
Endpoints for voice transcription and command processing.
Transcribe and command parser connect on Day 4.
"""

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter()


# Request schema for text-based endpoints
class TextRequest(BaseModel):
    text: str


# ============================================================
# TRANSCRIBE
# ============================================================

@router.post("/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Receive audio file, return transcript text."""
    # Day 4: Whisper processes the audio here
    return {
        "transcript": "placeholder - whisper not connected"
    }


# ============================================================
# COMMAND
# ============================================================

@router.post("/voice/command")
async def process_command(request: TextRequest):
    """Receive text, parse it into a command, execute it."""
    # Day 4: Command parser processes request.text here
    return {
        "text": request.text,
        "action": "none",
        "message": "command parser not connected"
    }


# ============================================================
# TEXT (shortcut)
# ============================================================

@router.post("/voice/text")
async def text_input(request: TextRequest):
    """Receive typed text, skip transcription, go straight to command processing."""
    # Day 4: Same as command, but this is the user-facing shortcut
    return {
        "text": request.text,
        "action": "none",
        "message": "command parser not connected"
    }
