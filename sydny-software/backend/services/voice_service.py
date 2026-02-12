"""
Voice Service
STT: Whisper (local) for speech-to-text
TTS: Native OS commands for text-to-speech
"""

import whisper
import subprocess
from platform_utils import CURRENT_PLATFORM

# Load Whisper model once at startup (base model ~140MB)
model = whisper.load_model("base")


def transcribe_audio(file_path: str) -> str:
    """Convert audio file to text using Whisper."""
    result = model.transcribe(file_path)
    return result["text"].strip()


def speak(text: str):
    """Speak text out loud using native OS TTS."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["say", text])
    elif CURRENT_PLATFORM == "windows":
        cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\')"'
        subprocess.run(cmd, shell=True)
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["espeak", text])
