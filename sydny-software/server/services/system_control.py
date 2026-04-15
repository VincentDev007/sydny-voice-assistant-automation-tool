import subprocess
import os
import shutil
import glob
from pathlib import Path
from utils.platform_utils import CURRENT_PLATFORM


def set_volume(level: int) -> str:
    if not 0 <= level <= 100:
        raise ValueError("Volume must be between 0 and 100")

    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows volume not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", f"{level}%"])

    return f"Volume set to {level}"


def mute() -> str:
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", "set volume with output muted"])
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows mute not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", "mute"])

    return "System muted"


def unmute() -> str:
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", "set volume without output muted"])
    elif CURRENT_PLATFORM == "windows":
        raise NotImplementedError("Windows unmute not yet implemented")
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["amixer", "set", "Master", "unmute"])

    return "System unmuted"


def shutdown_system() -> str:
    if CURRENT_PLATFORM == "mac":
        r = subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
    elif CURRENT_PLATFORM == "windows":
        r = subprocess.run(["shutdown", "/s", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        r = subprocess.run(["systemctl", "poweroff"])
    else:
        return "Shutdown not supported on this platform"

    return "Shutting down" if r.returncode == 0 else "Shutdown command failed"


def restart_system() -> str:
    if CURRENT_PLATFORM == "mac":
        r = subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'])
    elif CURRENT_PLATFORM == "windows":
        r = subprocess.run(["shutdown", "/r", "/t", "0"])
    elif CURRENT_PLATFORM == "linux":
        r = subprocess.run(["systemctl", "reboot"])
    else:
        return "Restart not supported on this platform"

    return "Restarting" if r.returncode == 0 else "Restart command failed"


def sleep_system() -> str:
    if CURRENT_PLATFORM == "mac":
        r = subprocess.run(["pmset", "sleepnow"])
    elif CURRENT_PLATFORM == "windows":
        r = subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif CURRENT_PLATFORM == "linux":
        r = subprocess.run(["systemctl", "suspend"])
    else:
        return "Sleep not supported on this platform"

    return "Going to sleep" if r.returncode == 0 else "Sleep command failed"


def open_app(app_name: str) -> str:
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["open", "-a", app_name])
    elif CURRENT_PLATFORM == "windows":
        subprocess.Popen(f"start {app_name}", shell=True)
    elif CURRENT_PLATFORM == "linux":
        subprocess.Popen([app_name])

    return f"Opened {app_name}"


def close_app(app_name: str) -> str:
    if CURRENT_PLATFORM == "mac":
        subprocess.run(["osascript", "-e", f'quit app "{app_name}"'])
    elif CURRENT_PLATFORM == "windows":
        subprocess.run(["taskkill", "/F", "/IM", f"{app_name}.exe"])
    elif CURRENT_PLATFORM == "linux":
        subprocess.run(["pkill", app_name])

    return f"Closed {app_name}"


def get_search_paths() -> list:
    home = Path.home()
    return [
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home,
    ]


def search_file(filename: str) -> list:
    matches = []
    for directory in get_search_paths():
        pattern = str(directory / "**" / filename)
        found = glob.glob(pattern, recursive=True)
        matches.extend(found)
        if len(matches) >= 10:
            break
    return matches[:10]


def open_file(filepath: str) -> str:
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
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source file not found: {source}")

    shutil.move(source, destination)
    return f"Moved {source} to {destination}"


def delete_file(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    os.remove(filepath)
    return f"Deleted {filepath}"


def execute_intent(intent: str, target: str = None):
    if intent == "open-app":
        open_app(target)
    elif intent == "close-app":
        close_app(target)
    elif intent == "volume":
        try:
            set_volume(int(target))
        except (ValueError, TypeError):
            print(f"[execute_intent] invalid volume target: {target}")
    elif intent == "mute":
        mute()
    elif intent == "unmute":
        unmute()
    elif intent == "shutdown":
        shutdown_system()
    elif intent == "restart":
        restart_system()
    elif intent == "sleep":
        sleep_system()
    elif intent == "open-file":
        open_file(target)
    elif intent == "delete-file":
        delete_file(target)
    elif intent == "search-file":
        results = search_file(target)
        print(f"[execute_intent] search-file results: {results}")
    else:
        print(f"[execute_intent] unhandled intent: {intent}")
