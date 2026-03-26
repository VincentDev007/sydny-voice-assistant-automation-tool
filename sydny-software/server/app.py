"""
SYDNY Backend API — app.py
===========================
Entry point for the Sydny v0.5.0 backend.
Starts FastAPI, creates the memory table, registers all routes.
"""

from contextlib import asynccontextmanager

# FastAPI — the web framework that handles HTTP requests and responses
from fastapi import FastAPI

# CORSMiddleware — allows the frontend (different port) to make requests to this backend
from fastapi.middleware.cors import CORSMiddleware

# engine — the database connection; Base — the parent class all database models inherit from
from database import engine, Base

# so SQLAlchemy can create the table. Even though we don't use `models` directly here,
# the import triggers the model registration with Base.
import models.memory_model

# Import all route modules — each handles a different group of endpoints
from routes import platform, system, voice


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SYDNY API",
    description="Backend API for SYDNY voice assistant",
    version="0.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


app.include_router(platform.router, prefix="/api")   # Platform detection
app.include_router(system.router, prefix="/api")     # System control (volume, apps, power, files)
app.include_router(voice.router)                     # Voice — prefix already set in routes/voice.py

