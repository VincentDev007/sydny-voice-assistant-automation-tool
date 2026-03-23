"""
SYDNY Backend API — app.py ; RENAME THIS main.py!!!!!!
===========================
This is the ENTRY POINT of the entire backend.
When you run `uvicorn app:app`, this is the file that runs.

WHAT IT DOES:
1. Creates a FastAPI application instance
2. Configures CORS (Cross-Origin Resource Sharing) so the frontend can talk to it
3. Creates the database tables when the server starts
4. Connects all route modules (platform, tasks, system, voice) under the /api prefix
5. Provides health check endpoints to verify the server is running

FLOW:
  dev.sh starts uvicorn → loads this file → creates app → registers routes → listens on port 8000

WHY CORS?
  The frontend (React) runs on localhost:1420, but the backend runs on localhost:8000.
  Browsers block requests between different ports by default (security feature).
  CORS tells the browser: "It's okay, allow requests from these origins."
  We allow two origins:
    - http://localhost:1420 → Vite dev server (during development)
    - tauri://localhost    → Tauri production app (after building)

WHY /api PREFIX?
  All routes are mounted under /api (e.g., /api/tasks, /api/voice/transcribe).
  This is a common convention to separate API routes from other URLs.
  It makes it clear which endpoints are API calls vs. regular pages.
"""

# FastAPI — the web framework that handles HTTP requests and responses
from fastapi import FastAPI

# CORSMiddleware — allows the frontend (different port) to make requests to this backend
from fastapi.middleware.cors import CORSMiddleware

# engine — the database connection; Base — the parent class all database models inherit from
from database import engine, Base

# models — importing this ensures Python knows about our Task model
# so SQLAlchemy can create the table. Even though we don't use `models` directly here,
# the import triggers the model registration with Base.
import models.tasks_models as tasks_models

# Import all route modules — each handles a different group of endpoints
from routes import platform, tasks, system, voice


# ============================================================
# CREATE THE APP
# ============================================================
# This creates the FastAPI application instance.
# Think of it as "turning on the server" — it doesn't listen yet,
# but it's ready to have routes and middleware added to it.
app = FastAPI(
    title="SYDNY API",                                    # Name shown in auto-generated docs at /docs
    description="Backend API for SYDNY voice assistant",  # Description in docs
    version="2.0.0"                                       # API version
)


# ============================================================
# CONFIGURE CORS (Cross-Origin Resource Sharing)
# ============================================================
# Without this, the browser would block ALL requests from the frontend
# because the frontend (port 1420) and backend (port 8000) are different "origins."
#
# allow_origins     → which websites can make requests to this API
# allow_credentials → allow cookies/auth headers to be sent
# allow_methods     → which HTTP methods are allowed (GET, POST, PUT, DELETE, etc.)
# allow_headers     → which HTTP headers the frontend can send
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],   # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers ; add more security here!!
)


# ============================================================
# DATABASE STARTUP ; this is outdated! use lifespan transition instead!!!
# ============================================================
# When the server starts, this creates all database tables if they don't exist yet.
# Base.metadata.create_all() looks at all models that inherit from Base (like Task)
# and creates their corresponding tables in the SQLite database.
#
# If the tables already exist, this does nothing — it's safe to call every startup.
@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise  # stop the server from starting


# ============================================================
# CONNECT ROUTE MODULES
# ============================================================
# Each route module handles a different group of endpoints.
# The prefix="/api" means all routes in each module will be under /api/...
#
# For example:
#   platform.router has @router.get("/platform")    → becomes GET  /api/platform
#   tasks.router    has @router.post("/tasks")       → becomes POST /api/tasks
#   system.router   has @router.post("/system/mute") → becomes POST /api/system/mute
#   voice.router    has @router.post("/voice/speak") → becomes POST /api/voice/speak
app.include_router(platform.router, prefix="/api")   # Platform detection
app.include_router(tasks.router, prefix="/api")      # Task CRUD operations
app.include_router(system.router, prefix="/api")     # System control (volume, apps, power, files)
app.include_router(voice.router, prefix="/api")      # Voice (transcribe, command parse, TTS)

