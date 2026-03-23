"""
System Control — system_control.py
====================================
Controls your computer: volume, power, apps, and files.
Cross-platform — uses the right commands for Mac, Windows, or Linux.

WHAT IT DOES:
  Provides Python functions that run system-level shell commands.
  Each function checks CURRENT_PLATFORM and runs the appropriate command.

WHY subprocess?
  Python can't directly control system volume or open apps.
  subprocess.run() lets us execute shell commands from Python.
  It's like typing a command in Terminal, but programmatically.

HOW IT CONNECTS:
  Voice command → command_parser.py → App.tsx → api.ts → routes/system.py → THIS FILE
  For example: "set volume to 50" → set-volume intent → api.setVolume(50) →
    POST /api/system/volume → system_control.set_volume(50) → osascript command

SECURITY NOTE:
  These functions execute real system commands. In SAFE MODE (frontend toggle),
  App.tsx blocks the API call before it reaches here. But in LIVE MODE,
  commands like shutdown_system() WILL actually shut down the computer.
"""

# subprocess — runs shell commands (like typing in Terminal)
import subprocess

# os — file system operations (check if files exist, delete files)
import os

# shutil — high-level file operations (move files across drives)
import shutil

# glob — find files matching a pattern (e.g., all .txt files in a folder)
import glob

# Path — modern Python file path handling (cleaner than string manipulation)
from pathlib import Path

# CURRENT_PLATFORM — "mac", "windows", or "linux" (detected once at startup)
from utils.platform_utils import CURRENT_PLATFORM


# ============================================================
# VOLUME CONTROL
# ============================================================

def set_volume(level: int) -> str:
    """
    Set system volume to a level between 0 and 100.

    Mac:     Uses `osascript` to run AppleScript commands.
             "set volume output volume 50" sets volume to 50%.
    Windows: Not yet implemented (would use pycaw or nircmd).
    Linux:   Uses `amixer` to control ALSA audio mixer.
             "amixer set Master 50%" sets master volume to 50%.
    """
    # Validate input — reject anything outside 0-100
    if not 0 <= level <= 100:
        raise ValueError("Volume must be between 0 and 100")

    if CURRENT_PLATFORM == "mac":
        # osascript runs AppleScript — macOS's built-in scripting language
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        # ADD WINDOWS VOLUME COMMANDS HERE!!
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows volume not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        # amixer is the ALSA (Advanced Linux Sound Architecture) mixer control
        subprocess.run(["amixer", "set", "Master", f"{level}%"])

    return f"Volume set to {level}"


def mute() -> str:
    """
    Mute system audio.

    Mac:   "set volume with output muted" → toggles mute ON via AppleScript
    Linux: "amixer set Master mute" → mutes the master channel via ALSA
    """
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", "set volume with output muted"])
    # ADD WINDOWS MUTE COMMANDS HERE!!
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows mute not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", "mute"])

    return "System muted"


def unmute() -> str:
    """
    Unmute system audio.

    Mac:   "set volume without output muted" → toggles mute OFF via AppleScript
    Linux: "amixer set Master unmute" → unmutes the master channel via ALSA
    """
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
# WARNING: These commands ACTUALLY control your computer's power state.
# The command parser flags these with needs_confirm=True so the user
# sees a confirmation dialog before execution.

def shutdown_system() -> str:
    """
    Shutdown the computer. THIS ACTUALLY SHUTS DOWN THE MACHINE.

    Mac:     AppleScript tells System Events to shut down
    Windows: `shutdown /s /t 0` → shutdown (/s) with 0 second delay (/t 0)
    Linux:   `systemctl poweroff` → systemd power off command
    """
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["shutdown", "/s", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["systemctl", "poweroff"])

    return "Shutting down"


def restart_system() -> str:
    """
    Restart the computer. THIS ACTUALLY RESTARTS THE MACHINE.

    Mac:     AppleScript tells System Events to restart
    Windows: `shutdown /r /t 0` → restart (/r) with 0 second delay (/t 0)
    Linux:   `systemctl reboot` → systemd reboot command
    """
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["shutdown", "/r", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["systemctl", "reboot"])

    return "Restarting"


def sleep_system() -> str:
    """
    Put the computer to sleep.

    Mac:     `pmset sleepnow` → macOS power management command
    Windows: `rundll32.exe powrprof.dll,SetSuspendState` → calls Windows power API
    Linux:   `systemctl suspend` → systemd suspend command
    """
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
    """
    Open an application by name.

    Mac:     `open -a Safari` → searches /Applications for the app and opens it
    Windows: `start Chrome` → uses Windows shell to find and open the app
    Linux:   Runs the binary directly (e.g., `firefox`)

    Example voice commands that trigger this:
      "Open Safari"  → open_app("safari")
      "Open Spotify" → open_app("spotify")
    """
    if CURRENT_PLATFORM == "mac":
        # `open -a` searches /Applications for the app name
        subprocess.run(["open", "-a", app_name])
    elif CURRENT_PLATFORM == "windows":
        # Popen is non-blocking — the app opens in a separate process
        subprocess.Popen(f"start {app_name}", shell=True)
    elif CURRENT_PLATFORM == "linux":
        subprocess.Popen([app_name])

    return f"Opened {app_name}"


def close_app(app_name: str) -> str:
    """
    Close an application by name.

    Mac:     AppleScript `quit app "Safari"` → asks the app to quit gracefully
    Windows: `taskkill /F /IM Safari.exe` → forcefully terminates the process
    Linux:   `pkill safari` → sends SIGTERM to matching processes

    Example voice commands:
      "Close Safari" → close_app("safari")
    """
    if CURRENT_PLATFORM == "mac":
        # AppleScript politely asks the app to quit (not force kill)
        subprocess.run(["osascript", "-e", f'quit app "{app_name}"'])
    elif CURRENT_PLATFORM == "windows":
        # /F = force terminate, /IM = match by image name (process name)
        subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"])
    elif CURRENT_PLATFORM == "linux":
        # pkill sends SIGTERM to all processes matching the name
        subprocess.run(["pkill", app_name])

    return f"Closed {app_name}"


# ============================================================
# FILE OPERATIONS
# ============================================================

def get_search_paths() -> list:
    """
    Returns common directories to search for files.
    Searches Desktop, Documents, Downloads, and the home folder.

    Path.home() returns the user's home directory:
      Mac:   /Users/username
      Win:   C:\\Users\\username
      Linux: /home/username
    """
    home = Path.home()
    return [
        home / "Desktop",     # Most common place users put files
        home / "Documents",   # Documents folder
        home / "Downloads",   # Downloads folder
        home,                 # Home directory (catches everything else)
    ]


def search_file(filename: str) -> list:
    """
    Search for a file in common directories.
    Returns a list of matching file paths (max 10 results).

    Uses glob patterns: "**" means "search all subdirectories recursively"
    So Desktop/**/report.txt finds report.txt anywhere under Desktop.

    Example voice commands:
      "Find report.txt" → search_file("report.txt")
      "Search homework" → search_file("homework")
    """
    matches = []
    for directory in get_search_paths():
        # Build a recursive search pattern: /Users/you/Desktop/**/filename
        pattern = str(directory / "**" / filename)
        # recursive=True makes ** work (search all subdirectories)
        found = glob.glob(pattern, recursive=True)
        matches.extend(found)
        # Stop early if we have enough results (performance optimization)
        if len(matches) >= 10:
            break
    return matches[:10]  # Return at most 10 results


def open_file(filepath: str) -> str:
    """
    Open a file with the system's default application.

    Mac:     `open report.pdf` → opens with Preview (or whatever is set as default)
    Windows: `os.startfile()` → uses Windows shell associations
    Linux:   `xdg-open report.pdf` → uses the desktop environment's default app

    Example voice commands:
      "Open file report.pdf" → open_file("report.pdf")
    """
    # Check if the file actually exists before trying to open it
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
    """
    Move a file from source to destination.

    Uses shutil.move() — works across drives/partitions (unlike os.rename()).
    Also works for renaming files (move to same directory with a different name).
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")

    shutil.move(source, destination)
    return f"Moved {source} to {destination}"


def delete_file(filepath: str) -> str:
    """
    Permanently delete a file. THIS IS IRREVERSIBLE — does NOT go to trash.

    Uses os.remove() which permanently deletes the file.
    The command parser flags "delete file" with needs_confirm=True,
    so the user sees a confirmation dialog before this runs.

    Example voice commands:
      "Delete file old-notes.txt" → delete_file("old-notes.txt")
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    os.remove(filepath)
    return f"Deleted {filepath}"
