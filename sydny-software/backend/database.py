"""
Database configuration for SYDNY
Uses SQLite for local storage
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL - creates sydny.db file in backend folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./sydny.db"

# Create database engine
# connect_args={"check_same_thread": False} is needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for database models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Creates a new database session for each request
    Automatically closes it when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()