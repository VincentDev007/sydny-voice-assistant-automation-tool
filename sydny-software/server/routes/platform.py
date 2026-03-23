"""
Platform Routes — routes/platform.py
======================================
Endpoint for checking what platform SYDNY is running on.

WHAT IT DOES:
  Provides a single GET endpoint that returns system info (OS, version, CPU architecture).
  Useful for diagnostics — lets the frontend know what system it's controlling.

ENDPOINT:
  GET /api/platform → returns OS info dict

HOW IT CONNECTS:
  Frontend api.ts could call this → FastAPI routes it here → calls platform_utils.get_platform_info()
"""

# APIRouter — creates a group of related endpoints that can be mounted on the main app
from fastapi import APIRouter

# get_platform_info — returns a dict with OS name, version, CPU architecture, etc.
from utils.platform_utils import get_platform_info

# Create a router for this module — gets mounted in app.py with prefix="/api"
router = APIRouter()


@router.get("/platform")
async def platform_info():
    """
    Returns what platform SYDNY is running on.

    Example response on macOS:
      {
        "platform": "mac",
        "system": "Darwin",
        "release": "23.1.0",
        "machine": "arm64",
        "mac_version": "14.1"
      }
    """
    return get_platform_info()
