"""
Database Models for SYDNY
Defines what a task looks like in the database.
v1.0.0 used a JSON file — v2.0.0 uses a real database.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class Task(Base):
    """
    Task model — represents the 'tasks' table in the database.
    
    v1.0.0 equivalent (from sydny_tasks.json):
    {"id": 1, "description": "Buy groceries", "priority": "normal", "completed": false, "created": "...", "completed_at": null}
    
    Same data, but now it lives in a real database table instead of a JSON file.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    priority = Column(String, default="normal")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)






