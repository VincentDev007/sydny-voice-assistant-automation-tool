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
