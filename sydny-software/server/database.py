"""
Database Configuration — database.py
======================================
Sets up the connection between Python and the SQLite database.

WHAT IT DOES:
1. Creates a "database engine" — the connection to the SQLite file (sydny.db)
2. Creates a "session factory" — generates sessions for each API request
3. Defines a "Base" class that all database models (like Task) must inherit from
4. Provides a get_db() function that FastAPI uses to inject database sessions into routes

KEY CONCEPTS:
  - Engine:  The connection to the database. Think of it as the phone line.
  - Session: A conversation with the database. Each API request gets its own session.
  - Base:    The parent class for all models. SQLAlchemy uses this to track all tables.

WHY SQLite?
  SQLite stores everything in a single file (sydny.db). No separate database server needed.
  Perfect for a local desktop app like SYDNY. The file lives in the backend/ folder.

WHY check_same_thread=False?
  SQLite normally only allows access from the thread that created the connection.
  FastAPI is async (multiple threads), so we need to disable this check.
  This is safe because SQLAlchemy manages its own thread safety via sessions.

WHY get_db() as a generator (yield)?
  FastAPI's "Depends" system calls get_db() for each request.
  The `yield` pauses the function, gives the session to the route, then
  the `finally` block runs after the route is done — closing the session.
  This guarantees every session is properly closed, even if an error occurs.
"""

# create_engine — creates the database connection
from sqlalchemy import create_engine

# declarative_base — creates the Base class that all models inherit from
from sqlalchemy.ext.declarative import declarative_base

# sessionmaker — creates a factory that produces new database sessions
from sqlalchemy.orm import sessionmaker


# ============================================================
# DATABASE CONNECTION
# ============================================================
# sqlite:///./sydny.db means:
#   sqlite:///  → use SQLite driver
#   ./sydny.db  → file is in the current directory (backend/)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sydny.db" # this is hard coded!!!

# Create the engine (database connection)
# check_same_thread=False → allows async FastAPI to use SQLite safely
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
) 

# ============================================================
# SESSION FACTORY
# ============================================================
# Creates a factory that produces new database sessions on demand.
# autocommit=False → we manually call db.commit() to save changes
# autoflush=False  → we manually control when changes are sent to the DB
# bind=engine      → sessions use our engine to talk to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================
# BASE CLASS
# ============================================================
# Every database model (like Task in models.py) inherits from this.
# SQLAlchemy uses Base to keep track of all models and their tables.
Base = declarative_base()


# ============================================================
# DATABASE SESSION DEPENDENCY
# ============================================================
# FastAPI calls this function for every route that needs database access.
# Routes declare they need it with: db: Session = Depends(get_db)
#
# HOW IT WORKS:
#   1. FastAPI calls get_db()
#   2. A new session is created (SessionLocal())
#   3. yield pauses here — the session is given to the route function
#   4. The route runs, uses the session (queries, inserts, etc.)
#   5. After the route finishes (or crashes), the finally block runs
#   6. The session is closed (db.close())
def get_db():
    """
    Creates a new database session for each request.
    Automatically closes it when done (even if there's an error).
    """
    db = SessionLocal()
    try:
        yield db       # ← Route gets the session here
    finally:
        db.close()     # ← Always runs, even if the route throws an error
