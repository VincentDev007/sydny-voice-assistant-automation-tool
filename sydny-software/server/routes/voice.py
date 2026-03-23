"""
Voice Routes — routes/voice.py
================================
Endpoints for voice transcription and command processing.
This is the heart of SYDNY's voice pipeline.

WHAT IT DOES:
  Provides 4 endpoints that handle the entire voice → action flow:
    POST /api/voice/transcribe → receives audio file, returns text (Speech-to-Text)
    POST /api/voice/command    → receives text, returns parsed intent (from voice input)
    POST /api/voice/text       → receives text, returns parsed intent (from typed input)
    POST /api/voice/speak      → receives text, speaks it out loud (Text-to-Speech)

THE VOICE PIPELINE:
  1. User clicks the HAL eye → browser records audio → sends WAV to /voice/transcribe
  2. Whisper transcribes audio → returns text (e.g., "open Safari")
  3. Frontend sends text to /voice/command → command_parser extracts intent
  4. Frontend executes the command → Sydny responds → calls /voice/speak
  5. macOS `say` command speaks Sydny's response out loud

WHY TWO SIMILAR ENDPOINTS (command vs text)?
  /voice/command → used after voice transcription (from mic input)
  /voice/text    → used for typed text input (from terminal input)
  They both call parse_command() — the separation is for clarity and future flexibility.

WHY TEMP FILES?
  Whisper needs a file path to read audio, but FastAPI receives the audio as bytes.
  We write the bytes to a temporary .wav file, give Whisper the path, then delete it.
  The `finally` block ensures the temp file is always cleaned up, even if Whisper crashes.
"""

# APIRouter — creates a group of related endpoints
# UploadFile — FastAPI's way of handling file uploads (multipart form data)
# File — marks a parameter as a file upload with File(...)
from fastapi import APIRouter, UploadFile, File

# BaseModel — for defining the shape of JSON request bodies
from pydantic import BaseModel

# tempfile — creates temporary files that we can pass to Whisper
import tempfile

# os — for deleting the temporary file after transcription
import os

# transcribe_audio — Whisper STT; speak — native OS TTS
from services.voice_service import transcribe_audio, speak

# parse_command — converts natural language text into {intent, target, needs_confirm}
from server.services.voice_command_parser import parse_command

# Create a router for this module — gets mounted in app.py with prefix="/api"
router = APIRouter()


# Request body schema for endpoints that receive text
class TextRequest(BaseModel):
    text: str    # The text to parse or speak


# ============================================================
# TRANSCRIBE — Speech-to-Text (STT)
# ============================================================

@router.post("/voice/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Receive an audio file (WAV format), return the transcribed text.

    FLOW:
      1. Frontend sends a WAV file as multipart form data
      2. We save it to a temp file (Whisper needs a file path, not raw bytes)
      3. Whisper's model.transcribe() converts speech → text
      4. We return the transcript and delete the temp file

    File(...) means the file parameter is REQUIRED — FastAPI returns 422 if missing.
    delete=False in NamedTemporaryFile because we need the file to exist when Whisper reads it.
    We manually delete it in the `finally` block after transcription.
    """
    # Create a temp file with .wav extension (Whisper expects WAV format)
    # delete=False → don't auto-delete when closed; we'll delete manually
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        # Read the uploaded file bytes and write to temp file
        content = await file.read()
        temp.write(content)
        temp.close()  # Close so Whisper can open it

        # Run Whisper transcription on the temp file
        transcript = transcribe_audio(temp.name)
        return {"transcript": transcript}
    finally:
        # Always clean up the temp file, even if transcription fails
        os.unlink(temp.name)


# ============================================================
# COMMAND — Parse voice transcription into intent
# ============================================================

@router.post("/voice/command")
async def process_command(request: TextRequest):
    """
    Receive text (from voice transcription), parse it into a command.

    This is Step 2 of the voice pipeline:
      Audio → /transcribe → text → /command → {intent, target, needs_confirm}

    Example:
      Input:  {"text": "open Safari"}
      Output: {"text": "open Safari", "intent": "open-app", "target": "safari", "needs_confirm": false}
    """
    result = parse_command(request.text)
    return {
        "text": request.text,                    # Echo back the original text
        "intent": result["intent"],              # What action to take (e.g., "open-app")
        "target": result["target"],              # What to act on (e.g., "safari")
        "needs_confirm": result["needs_confirm"] # Does the user need to confirm? (for dangerous ops)
    }


# ============================================================
# TEXT — Parse typed text into intent (shortcut)
# ============================================================

@router.post("/voice/text")
async def text_input(request: TextRequest):
    """
    Receive typed text, parse and return command.
    Same as /voice/command but for keyboard input instead of voice.

    Example:
      Input:  {"text": "add task buy groceries"}
      Output: {"text": "add task buy groceries", "intent": "add-task",
               "target": "buy groceries|normal", "needs_confirm": false}
    """
    result = parse_command(request.text)
    return {
        "text": request.text,
        "intent": result["intent"],
        "target": result["target"],
        "needs_confirm": result["needs_confirm"]
    }


# ============================================================
# SPEAK — Text-to-Speech (TTS)
# ============================================================

@router.post("/voice/speak")
async def speak_text(request: TextRequest):
    """
    Speak text out loud using the native OS text-to-speech engine.

    On macOS, this runs the `say` command.
    Only used for SYDNY's responses — the user's transcript is NOT spoken back.

    Example:
      Input:  {"text": "Opening Safari."}
      Result: macOS speaks "Opening Safari." out loud
      Output: {"status": "ok", "text": "Opening Safari."}
    """
    speak(request.text)
    return {"status": "ok", "text": request.text}
