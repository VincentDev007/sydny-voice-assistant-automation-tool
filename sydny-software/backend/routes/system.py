"""
System Control Routes
API endpoints for controlling the computer.
Wraps system_control.py functions as HTTP endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import system_control

router = APIRouter()


class VolumeRequest(BaseModel):
    level: int

class AppRequest(BaseModel):
    app_name: str

class FileRequest(BaseModel):
    filepath: str

class MoveFileRequest(BaseModel):
    source: str
    destination: str

class SearchRequest(BaseModel):
    filename: str

# ============================================================
# VOLUME
# ============================================================

@router.post("/system/volume")
async def set_volume(request: VolumeRequest):
    """Set volume to a level between 0 and 100."""
    try:
        result = system_control.set_volume(request.level)
        return {"message": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/system/mute")
async def mute():
    """Mute system audio."""
    result = system_control.mute()
    return {"message": result}


@router.post("/system/unmute")
async def unmute():
    """Unmute system audio."""
    result = system_control.unmute()
    return {"message": result}

# ============================================================
# POWER
# ============================================================

@router.post("/system/shutdown")
async def shutdown():
    """Shutdown the computer."""
    result = system_control.shutdown_system()
    return {"message": result}


@router.post("/system/restart")
async def restart():
    """Restart the computer."""
    result = system_control.restart_system()
    return {"message": result}


@router.post("/system/sleep")
async def sleep():
    """Put the computer to sleep."""
    result = system_control.sleep_system()
    return {"message": result}

# ============================================================
# APPLICATIONS
# ============================================================

@router.post("/system/open-app")
async def open_app(request: AppRequest):
    """Open an application by name."""
    result = system_control.open_app(request.app_name)
    return {"message": result}


@router.post("/system/close-app")
async def close_app(request: AppRequest):
    """Close an application by name."""
    result = system_control.close_app(request.app_name)
    return {"message": result}


# ============================================================
# FILES
# ============================================================

@router.post("/system/search-file")
async def search_file(request: SearchRequest):
    """Search for a file by name."""
    matches = system_control.search_file(request.filename)
    return {"matches": matches}


@router.post("/system/open-file")
async def open_file(request: FileRequest):
    """Open a file with its default application."""
    try:
        result = system_control.open_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/move-file")
async def move_file(request: MoveFileRequest):
    """Move a file from source to destination."""
    try:
        result = system_control.move_file(request.source, request.destination)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/delete-file")
async def delete_file(request: FileRequest):
    """Permanently delete a file."""
    try:
        result = system_control.delete_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
