"""
Database Models — models.py
============================
Defines what data looks like in the database using Python classes.
Each class = one table. Each attribute = one column.

WHAT IT DOES:
  Defines the Task model — the only table in SYDNY's database.
  SQLAlchemy reads this class and creates a "tasks" table with these columns:
    id, description, priority, completed, created_at, completed_at

v1.0.0 vs v2.0.0:
  v1.0.0 stored tasks in a JSON file (sydny_tasks.json) — read/write the whole file every time.
  v2.0.0 uses a real database (SQLite) — faster, safer, supports queries.

HOW IT CONNECTS:
  models.py defines the SHAPE of data (what columns exist)
  schemas.py defines the RULES for data (what's required, what types are allowed)
  routes/tasks.py uses both to handle API requests
"""

# Column types — define what kind of data each column holds
from sqlalchemy import Column, Integer, String, Boolean, DateTime

# datetime — for timestamps (when a task was created/completed)
from datetime import datetime

# Base — the parent class from database.py that all models must inherit
from database import Base


class Task(Base):
    """
    Task model — represents the 'tasks' table in the database.

    This is an ORM (Object-Relational Mapping) model:
      - Instead of writing SQL: INSERT INTO tasks (description, priority) VALUES ('Buy milk', 'normal')
      - We write Python:       task = Task(description='Buy milk', priority='normal')
      - SQLAlchemy translates between the two automatically.

    v1.0.0 equivalent (from sydny_tasks.json):
      {"id": 1, "description": "Buy groceries", "priority": "normal",
       "completed": false, "created": "...", "completed_at": null}

    Same data, but now it lives in a real database table instead of a JSON file.
    """

    # __tablename__ tells SQLAlchemy what to name the table in the database
    __tablename__ = "tasks"

    # id — unique identifier, auto-increments (1, 2, 3, ...)
    # primary_key=True → this is the unique identifier for each row
    # index=True       → creates an index for faster lookups by ID
    id = Column(Integer, primary_key=True, index=True)

    # description — what the task is (e.g., "Buy groceries")
    # nullable=False → every task MUST have a description
    description = Column(String, nullable=False)

    # priority — how important the task is: "low", "normal", or "high"
    # default="normal" → if not specified, defaults to "normal"
    priority = Column(String, default="normal")

    # completed — whether the task is done or not
    # default=False → new tasks start as not completed
    completed = Column(Boolean, default=False)

    # created_at — when the task was created (auto-set to current time)
    # default=datetime.utcnow → automatically records the creation time
    created_at = Column(DateTime, default=datetime.utcnow)

    # completed_at — when the task was marked as done (null if not completed yet)
    # nullable=True → this can be empty (null) until the task is completed
    completed_at = Column(DateTime, nullable=True)
