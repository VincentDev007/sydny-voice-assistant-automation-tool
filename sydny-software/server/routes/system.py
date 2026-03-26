"""
System Control Routes — routes/system.py
==========================================
API endpoints for controlling the computer.
Wraps system_control.py functions as HTTP endpoints.

WHAT IT DOES:
  Acts as the HTTP layer between the frontend and system_control.py.
  The frontend sends a POST request → this file receives it → calls the right
  function in system_control.py → returns the result as JSON.

  Think of it like a waiter:
    system_control.py = the kitchen (does the actual work)
    system.py         = the waiter (takes orders, delivers results)

ENDPOINTS:
  Volume:
    POST /api/system/volume      → set volume (0-100)
    POST /api/system/mute        → mute audio
    POST /api/system/unmute      → unmute audio

  Power:
    POST /api/system/shutdown    → shutdown computer
    POST /api/system/restart     → restart computer
    POST /api/system/sleep       → put computer to sleep

  Apps:
    POST /api/system/open-app    → open an application
    POST /api/system/close-app   → close an application

  Files:
    POST /api/system/search-file → search for a file
    POST /api/system/open-file   → open a file
    POST /api/system/move-file   → move a file
    POST /api/system/delete-file → delete a file

WHY POST for everything (instead of GET)?
  POST requests carry a JSON body, which we need for sending data like
  volume level, app name, or file path. GET requests can only send data
  in the URL, which is limited and messy for complex data.

HOW IT CONNECTS:
  Frontend api.ts → POST /api/system/volume → THIS FILE → system_control.set_volume() → osascript
"""

# APIRouter — creates a group of related endpoints
# HTTPException — for returning error responses (like 404 File Not Found)
from fastapi import APIRouter, HTTPException

# BaseModel — for defining the shape of request bodies
from pydantic import BaseModel

from schemas.system_schemas import VolumeRequest, AppRequest, FileRequest, MoveFileRequest, SearchRequest

# system_control — the module that actually runs system commands
import services.system_control as system_control

# Create a router for this module — gets mounted in app.py with prefix="/api"
router = APIRouter()

# ============================================================
# VOLUME
# ============================================================

@router.post("/system/volume")
async def set_volume(request: VolumeRequest):
    """
    Set volume to a level between 0 and 100.

    Example request body: {"level": 50}
    Catches ValueError if level is outside 0-100 range.
    """
    try:
        result = system_control.set_volume(request.level)
        return {"message": result}
    except ValueError as e:
        # Return 400 Bad Request if volume is out of range
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/system/mute")
async def mute():
    """Mute system audio. No request body needed."""
    result = system_control.mute()
    return {"message": result}


@router.post("/system/unmute")
async def unmute():
    """Unmute system audio. No request body needed."""
    result = system_control.unmute()
    return {"message": result}


# ============================================================
# POWER
# ============================================================
# These endpoints are DANGEROUS — they actually control power state.
# The command parser flags them with needs_confirm=True so the user
# sees a confirmation dialog in the UI before these are called.

@router.post("/system/shutdown")
async def shutdown():
    """Shutdown the computer. No request body needed."""
    result = system_control.shutdown_system()
    return {"message": result}


@router.post("/system/restart")
async def restart():
    """Restart the computer. No request body needed."""
    result = system_control.restart_system()
    return {"message": result}


@router.post("/system/sleep")
async def sleep():
    """Put the computer to sleep. No request body needed."""
    result = system_control.sleep_system()
    return {"message": result}


# ============================================================
# APPLICATIONS
# ============================================================

@router.post("/system/open-app")
async def open_app(request: AppRequest):
    """
    Open an application by name.
    Example request body: {"app_name": "Safari"}
    """
    result = system_control.open_app(request.app_name)
    return {"message": result}


@router.post("/system/close-app")
async def close_app(request: AppRequest):
    """
    Close an application by name.
    Example request body: {"app_name": "Safari"}
    """
    result = system_control.close_app(request.app_name)
    return {"message": result}


# ============================================================
# FILES
# ============================================================

@router.post("/system/search-file")
async def search_file(request: SearchRequest):
    """
    Search for a file by name in common directories.
    Returns up to 10 matching file paths.
    Example request body: {"filename": "report.pdf"}
    """
    matches = system_control.search_file(request.filename)
    return {"matches": matches}


@router.post("/system/open-file")
async def open_file(request: FileRequest):
    """
    Open a file with its default application.
    Example request body: {"filepath": "/Users/you/Desktop/report.pdf"}
    Returns 404 if the file doesn't exist.
    """
    try:
        result = system_control.open_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/move-file")
async def move_file(request: MoveFileRequest):
    """
    Move a file from source to destination.
    Example request body: {"source": "/path/to/file.txt", "destination": "/new/path/file.txt"}
    Returns 404 if the source file doesn't exist.
    """
    try:
        result = system_control.move_file(request.source, request.destination)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/delete-file")
async def delete_file(request: FileRequest):
    """
    Permanently delete a file. THIS IS IRREVERSIBLE.
    Example request body: {"filepath": "/path/to/file.txt"}
    Returns 404 if the file doesn't exist.
    """
    try:
        result = system_control.delete_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


def execute_intent(intent: str, target: str = None):
    if intent == "open-app":
        open_app(target)
    elif intent == "close-app":
        close_app(target)
    elif intent == "volume":
        set_volume(int(target))
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
        search_file(target)
