import platform
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

_home = Path.home()
_system = platform.system()
if _system == "Darwin":
    _db_dir = _home / "Library" / "Application Support" / "Sydny"
elif _system == "Windows":
    _db_dir = _home / "AppData" / "Roaming" / "Sydny"
else:
    _db_dir = _home / ".local" / "share" / "Sydny"
_db_dir.mkdir(parents=True, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_dir}/sydny.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
