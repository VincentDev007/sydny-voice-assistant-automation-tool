from faster_whisper import WhisperModel
import subprocess
from utils.platform_utils import CURRENT_PLATFORM

model = WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_audio(file_path: str) -> str:
    segments, _ = model.transcribe(file_path)
    return " ".join(segment.text for segment in segments).strip()


def speak(text: str):
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["say", text])
    elif CURRENT_PLATFORM == "windows":
        cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak(\'{text}\')"'
        subprocess.run(cmd, shell=True)
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["espeak", text])
