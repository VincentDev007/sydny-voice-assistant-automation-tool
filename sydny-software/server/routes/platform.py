from fastapi import APIRouter
from utils.platform_utils import get_platform_info

router = APIRouter()


@router.get("/platform")
async def platform_info():
    return get_platform_info()
