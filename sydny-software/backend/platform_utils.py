"""
Platform Detection for SYDNY
Answers one question: "What computer am I running on?"
The rest of the code uses this to decide which commands to run.
"""

import platform

def get_platform() -> str:
    """
    Returns 'mac', 'windows', or 'linux'.
    Raises RuntimeError on unsupported platforms.
    """
    system = platform.system().lower()

    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    
def get_platform_info() -> dict:
    """
    Returns a dict with detailed platform info for diagnostics.
    """
    system = get_platform()

    info = {
        "platform": system,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    if system == "mac":
        info["mac_version"] = platform.mac_ver()[0]
    elif system == "windows":
        info["windows_version"] = platform.win32_ver()[1]

    return info

CURRENT_PLATFORM = get_platform()


