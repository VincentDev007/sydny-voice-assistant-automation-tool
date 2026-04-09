from fastapi import APIRouter, HTTPException
from schemas.system_schemas import VolumeRequest, AppRequest, FileRequest, MoveFileRequest, SearchRequest
import services.system_control as system_control

router = APIRouter()


@router.post("/system/volume")
async def set_volume(request: VolumeRequest):
    try:
        result = system_control.set_volume(request.level)
        return {"message": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/system/mute")
async def mute():
    result = system_control.mute()
    return {"message": result}


@router.post("/system/unmute")
async def unmute():
    result = system_control.unmute()
    return {"message": result}


@router.post("/system/shutdown")
async def shutdown():
    result = system_control.shutdown_system()
    return {"message": result}


@router.post("/system/restart")
async def restart():
    result = system_control.restart_system()
    return {"message": result}


@router.post("/system/sleep")
async def sleep():
    result = system_control.sleep_system()
    return {"message": result}


@router.post("/system/open-app")
async def open_app(request: AppRequest):
    result = system_control.open_app(request.app_name)
    return {"message": result}


@router.post("/system/close-app")
async def close_app(request: AppRequest):
    result = system_control.close_app(request.app_name)
    return {"message": result}


@router.post("/system/search-file")
async def search_file(request: SearchRequest):
    matches = system_control.search_file(request.filename)
    return {"matches": matches}


@router.post("/system/open-file")
async def open_file(request: FileRequest):
    try:
        result = system_control.open_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/move-file")
async def move_file(request: MoveFileRequest):
    try:
        result = system_control.move_file(request.source, request.destination)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/system/delete-file")
async def delete_file(request: FileRequest):
    try:
        result = system_control.delete_file(request.filepath)
        return {"message": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
