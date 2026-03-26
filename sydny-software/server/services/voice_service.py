"""
Voice Service — services/voice_service.py
==========================================
Handles both directions of voice for Sydny:
  STT: faster-whisper converts audio → text
  TTS: native OS commands convert text → speech
"""

# whisper — OpenAI's speech recognition model (runs locally, no API key needed)
from faster_whisper import WhisperModel

# subprocess — for running shell commands (the `say` command for TTS)
import subprocess

# CURRENT_PLATFORM — "mac", "windows", or "linux" (from platform_utils.py)
from utils.platform_utils import CURRENT_PLATFORM


# ============================================================
# LOAD WHISPER MODEL (runs once at server startup)
# ============================================================
# faster-whisper uses CTranslate2 C++ backend — 4x faster than openai-whisper
# device="cpu" — runs on CPU (no GPU needed)
# compute_type="int8" — quantized model, faster and uses less memory
model = WhisperModel("small", device="cpu", compute_type="int8")


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
    segments, _ = model.transcribe(file_path)
    return " ".join(segment.text for segment in segments).strip()


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
