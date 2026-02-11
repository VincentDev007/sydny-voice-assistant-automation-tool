"""
SYDNY Backend API
FastAPI application for voice assistant system
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routes import platform, tasks, system, voice   # ← add voice


# Create FastAPI app instance
app = FastAPI(
    title="SYDNY API",
    description="Backend API for SYDNY voice assistant",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# Connect routers
app.include_router(platform.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(voice.router, prefix="/api")    # ← add this

# General health endpoints
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "SYDNY API is running",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sydny-backend"
    }
