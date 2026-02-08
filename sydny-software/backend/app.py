"""
SYDNY Backend API
FastAPI application for voice assistant system
"""

from database import engine, Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="SYDNY API",
    description="Backend API for SYDNY voice assistant",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],  # Tauri's URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE) red flag alert!!
    allow_headers=["*"],  # Allow all headers red flag alert!!
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    """
    Creates all database tables when the app starts
    """
    Base.metadata.create_all(bind=engine)

# Health check api endpoint
@app.get("/")
async def root():
    """
    Root endpoint - simple health check
    Returns basic API information
    """
    return {
        "status": "online",
        "message": "SYDNY API is running",
        "version": "2.0.0"
    }

@app.get("/api/health")
async def health_check():
    """
    Dedicated health check endpoint
    Used by frontend to verify backend is reachable
    """
    return {
        "status": "healthy",
        "service": "sydny-backend"
    }