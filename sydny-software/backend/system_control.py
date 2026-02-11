"""
System Control for SYDNY
Controls your computer: volume, power, apps, and files.
Cross-platform — uses the right commands for Mac, Windows, or Linux.
"""

import subprocess
import os
import shutil
import glob
from pathlib import Path
from platform_utils import CURRENT_PLATFORM

# ============================================================
# VOLUME CONTROL
# ============================================================

def set_volume(level: int) -> str:
    """Set system volume to a level between 0 and 100."""
    if not 0 <= level <= 100:
        raise ValueError("Volume must be between 0 and 100")

    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
    elif CURRENT_PLATFORM == "windows":
        # Windows uses pycaw or nircmd — handled in future Windows setup
        raise NotImplementedError("Windows volume not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", f"{level}%"])

    return f"Volume set to {level}"


def mute() -> str:
    """Mute system audio."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", "set volume with output muted"])
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows mute not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", "mute"])

    return "System muted"


def unmute() -> str:
    """Unmute system audio."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", "set volume without output muted"])
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows unmute not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", "unmute"])

    return "System unmuted"

# ============================================================
# POWER MANAGEMENT
# ============================================================

def shutdown_system() -> str:
    """Shutdown the computer."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["shutdown", "/s", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["systemctl", "poweroff"])

    return "Shutting down"


def restart_system() -> str:
    """Restart the computer."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["shutdown", "/r", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["systemctl", "reboot"])

    return "Restarting"


def sleep_system() -> str:
    """Put the computer to sleep."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["pmset", "sleepnow"])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["systemctl", "suspend"])

    return "Going to sleep"

# ============================================================
# APPLICATION CONTROL
# ============================================================

def open_app(app_name: str) -> str:
    """Open an application by name."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["open", "-a", app_name])
    elif CURRENT_PLATFORM == "windows":
        subprocess.Popen(f"start {app_name}", shell=True)
    elif CURRENT_PLATFORM == "linux":
        subprocess.Popen([app_name])

    return f"Opened {app_name}"


def close_app(app_name: str) -> str:
    """Close an application by name."""
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", f'quit app "{app_name}"'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["pkill", app_name])

    return f"Closed {app_name}"

# ============================================================
# FILE OPERATIONS
# ============================================================

def get_search_paths() -> list:
    """Returns common directories to search for files."""
    home = Path.home()
    return [
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home,
    ]

def search_file(filename: str) -> list:
    """Search for a file in common directories. Returns list of matches."""
    matches = []
    for directory in get_search_paths():
        pattern = str(directory / "**" / filename)
        found = glob.glob(pattern, recursive=True)
        matches.extend(found)
        if len(matches) >= 10:
            break
    return matches[:10]

def open_file(filepath: str) -> str:
    """Open a file with the system's default application."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if CURRENT_PLATFORM == "mac":
        subprocess.run(["open", filepath])
    elif CURRENT_PLATFORM == "windows":
        os.startfile(filepath)
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["xdg-open", filepath])

    return f"Opened {filepath}"


def move_file(source: str, destination: str) -> str:
    """Move a file from source to destination."""
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")

    shutil.move(source, destination)
    return f"Moved {source} to {destination}"


def delete_file(filepath: str) -> str:
    """Permanently delete a file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    os.remove(filepath)
    return f"Deleted {filepath}"




