"""
Platform Routes
Endpoint for checking what platform SYDNY is running on.
"""

from fastapi import APIRouter
from platform_utils import get_platform_info

router = APIRouter()

@router.get("/platform")
async def platform_info():
    """Returns what platform SYDNY is running on."""
    return get_platform_info()
