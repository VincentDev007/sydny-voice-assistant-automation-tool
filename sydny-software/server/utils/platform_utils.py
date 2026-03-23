"""
Platform Detection — platform_utils.py
========================================
Answers one question: "What computer am I running on?"
The rest of the code uses this to decide which commands to run.

WHY THIS EXISTS:
  Mac, Windows, and Linux all use different commands for the same thing:
    - Set volume:    Mac uses `osascript`, Linux uses `amixer`
    - Open an app:   Mac uses `open -a`, Linux uses the binary name directly
    - Text-to-speech: Mac uses `say`, Linux uses `espeak`

  This file detects the OS ONCE at startup, and stores it in CURRENT_PLATFORM.
  Every other file imports CURRENT_PLATFORM and uses it in if/elif blocks.

HOW IT CONNECTS:
  platform_utils.py is imported by:
    - system_control.py  → to pick the right volume/power/app/file commands
    - voice_service.py   → to pick the right TTS command (say vs espeak)
"""

# platform — Python's built-in module for detecting the operating system
import platform


def get_platform() -> str:
    """
    Returns 'mac', 'windows', or 'linux'.
    Raises RuntimeError on unsupported platforms.

    Python's platform.system() returns:
      'Darwin'  → macOS (Darwin is the name of macOS's kernel)
      'Windows' → Windows
      'Linux'   → Linux
    We convert these to simpler, lowercase names for consistency.
    """
    system = platform.system().lower()

    if system == "darwin":       # macOS reports itself as "Darwin" (the kernel name)
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def get_platform_info() -> dict:
    """
    Returns a dictionary with detailed platform info for diagnostics.
    Used by the GET /api/platform endpoint (routes/platform.py).

    Example return value on macOS:
      {
        "platform": "mac",
        "system": "Darwin",
        "release": "23.1.0",
        "version": "Darwin Kernel Version 23.1.0",
        "machine": "arm64",
        "processor": "arm",
        "mac_version": "14.1"
      }
    """
    system = get_platform()

    info = {
        "platform": system,                  # Our simplified name (mac/windows/linux)
        "system": platform.system(),         # Raw OS name (Darwin/Windows/Linux)
        "release": platform.release(),       # Kernel version number
        "version": platform.version(),       # Full kernel version string
        "machine": platform.machine(),       # CPU architecture (arm64, x86_64, etc.)
        "processor": platform.processor(),   # Processor type
    }

    # Add OS-specific version info
    if system == "mac":
        info["mac_version"] = platform.mac_ver()[0]       # e.g., "14.1"
    elif system == "windows":
        info["windows_version"] = platform.win32_ver()[1] # e.g., "10.0.19041"

    return info


# ============================================================
# DETECT PLATFORM AT IMPORT TIME
# ============================================================
# This runs ONCE when the module is first imported.
# Every other file can just do: from platform_utils import CURRENT_PLATFORM
# and get "mac", "windows", or "linux" without calling a function each time.
CURRENT_PLATFORM = get_platform()
