"""
Voice Service — services/voice_service.py
==========================================
The voice engine of SYDNY.
Handles both directions of voice:
  STT (Speech-to-Text): Whisper converts audio → text
  TTS (Text-to-Speech): Native OS commands convert text → speech

WHAT IT DOES:
  transcribe_audio() → takes a .wav file path, returns the transcribed text
  speak()           → takes text, speaks it out loud using the OS TTS engine

WHY WHISPER (LOCAL)?
  OpenAI's Whisper runs entirely on your machine — no API key, no internet needed.
  The "small" model (~460MB) balances accuracy and speed.
  Available models: tiny (39MB) < base (140MB) < small (460MB) < medium (1.5GB) < large (3GB)
  We upgraded from "base" to "small" on Day 5 for better recognition accuracy.

WHY NATIVE TTS?
  Each OS has a built-in text-to-speech engine:
    Mac:     `say` command — uses the system voice
    Windows: PowerShell's SpeechSynthesizer — .NET built-in
    Linux:   `espeak` — open-source TTS engine
  No extra libraries or API keys needed.

HOW IT CONNECTS:
  routes/voice.py calls transcribe_audio() and speak()
  App.tsx's sydnySay() → api.speakText() → /api/voice/speak → speak() → macOS `say`
"""

# whisper — OpenAI's speech recognition model (runs locally, no API key needed)
import whisper

# subprocess — for running shell commands (the `say` command for TTS)
import subprocess

# CURRENT_PLATFORM — "mac", "windows", or "linux" (from platform_utils.py)
from utils.platform_utils import CURRENT_PLATFORM


# ============================================================
# LOAD WHISPER MODEL (runs once at server startup)
# ============================================================
# This loads the Whisper "small" model into memory.
# It only runs once — when the backend starts (when this module is first imported).
# The model stays in memory for the lifetime of the server.
#
# Model sizes:
#   "tiny"   → ~39MB,  fastest but least accurate
#   "base"   → ~140MB, decent for clear speech
#   "small"  → ~460MB, good balance of speed and accuracy ← WE USE THIS
#   "medium" → ~1.5GB, very accurate but slower
#   "large"  → ~3GB,   most accurate but requires lots of RAM
#
# The model is cached in ~/.cache/whisper/ after first download.
model = whisper.load_model("small")


def transcribe_audio(file_path: str) -> str:
    """
    Convert an audio file to text using Whisper.

    HOW IT WORKS:
      1. Whisper loads the audio file (must be a format ffmpeg can read — WAV, MP3, etc.)
      2. The audio is processed through the neural network
      3. The model outputs a dict with "text" (the transcript) and other metadata
      4. We return just the text, stripped of whitespace

    IMPORTANT:
      - The file must be in a format Whisper/ffmpeg can decode (WAV is safest)
      - The frontend converts browser audio (WebM) to WAV before sending
      - Whisper uses ffmpeg under the hood, so ffmpeg must be installed

    Args:
        file_path: Path to the audio file (usually a temp .wav file)

    Returns:
        The transcribed text as a string
    """
    result = model.transcribe(file_path)
    return result["text"].strip()


def speak(text: str):
    """
    Speak text out loud using the native OS text-to-speech engine.

    This is a BLOCKING call — the function doesn't return until the speech finishes.
    Only used for Sydny's responses, NOT for reading back the user's transcript.

    Platform commands:
      Mac:     `say "Hello"` → uses the default macOS system voice
      Windows: PowerShell → loads .NET SpeechSynthesizer and calls .Speak()
      Linux:   `espeak "Hello"` → open-source TTS engine (must be installed)

    Args:
        text: The text to speak out loud
    """
    if CURRENT_PLATFORM == "mac":
        # macOS built-in `say` command — uses the system default voice
        subprocess.run(["say", text])
    elif CURRENT_PLATFORM == "windows":
        # Windows: Use PowerShell to access .NET's built-in speech synthesis
        # Add-Type loads the System.Speech assembly
        # SpeechSynthesizer.Speak() is the Windows TTS API
        cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\')"'
        subprocess.run(cmd, shell=True)
    elif CURRENT_PLATFORM == "linux":
        # espeak is an open-source TTS engine for Linux
        # Must be installed: sudo apt install espeak
        subprocess.run(["espeak", text])
