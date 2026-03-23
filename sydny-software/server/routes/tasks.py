"""
Task Routes — routes/tasks.py
===============================
CRUD endpoints for managing tasks.
This is the bridge between the frontend and the database.

WHAT IT DOES:
  Provides 5 endpoints for full task management:
    POST   /api/tasks          → Create a new task
    GET    /api/tasks          → Get all tasks
    GET    /api/tasks/{id}     → Get a single task by ID
    PUT    /api/tasks/{id}     → Update a task (description, priority, or completion)
    DELETE /api/tasks/{id}     → Delete a task permanently

HOW IT CONNECTS:
  Frontend (api.ts) → HTTP request → FastAPI routes it here → validates with schemas.py →
    reads/writes via models.py → returns JSON response to frontend

  Three files work together:
    schemas.py → validates incoming data (the bouncer)
    models.py  → talks to the database (the filing cabinet)
    tasks.py   → glues them together (the receptionist)

KEY CONCEPTS:
  Depends(get_db) → FastAPI "dependency injection" — automatically creates a database
                     session for each request and closes it when done.
  response_model  → tells FastAPI what shape the response should be (TaskResponse),
                     so it automatically converts ORM objects to JSON.
  HTTPException   → sends a proper error response (like 404 Not Found) back to the frontend.
"""

# APIRouter — creates a group of related endpoints
# Depends — FastAPI's dependency injection system (auto-provides db sessions)
# HTTPException — for returning error responses (404, 400, etc.)
from fastapi import APIRouter, Depends, HTTPException

# Session — type hint for database sessions
from sqlalchemy.orm import Session

# get_db — the generator function that provides database sessions (from database.py)
from database import get_db

# Task — the ORM model that maps to the 'tasks' table (from models.py)
from models.tasks_models import Task

# Schemas — validation rules for incoming/outgoing data (from schemas.py)
from schemas.tasks_schemas import TaskCreate, TaskUpdate, TaskResponse

# List — type hint for returning a list of TaskResponse objects
from typing import List

# Create a router for this module — gets mounted in app.py with prefix="/api"
router = APIRouter()


# ============================================================
# CREATE — POST /api/tasks
# ============================================================
@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.

    1. FastAPI receives a POST request with JSON body
    2. Pydantic validates the body against TaskCreate schema
    3. We create a Task ORM object from the validated data
    4. db.add() stages the new task in the session
    5. db.commit() writes it to the database
    6. db.refresh() reloads the object to get auto-generated fields (id, created_at)
    7. Return the task — FastAPI converts it to JSON using TaskResponse
    """
    # Create an ORM Task object from the validated Pydantic schema
    db_task = Task(
        description=task.description,
        priority=task.priority
    )
    db.add(db_task)       # Stage the task for insertion
    db.commit()           # Write to the database
    db.refresh(db_task)   # Reload to get auto-generated fields (id, created_at)
    return db_task


# ============================================================
# READ ALL — GET /api/tasks
# ============================================================
@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(db: Session = Depends(get_db)):
    """
    Get all tasks.

    db.query(Task).all() is the SQLAlchemy equivalent of: SELECT * FROM tasks
    Returns a list of all tasks, which FastAPI converts to JSON.
    """
    tasks = db.query(Task).all()   # SELECT * FROM tasks
    return tasks


# ============================================================
# READ ONE — GET /api/tasks/{task_id}
# ============================================================
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a single task by ID.

    .filter(Task.id == task_id) is like: WHERE id = ?
    .first() returns the first match or None if not found.
    If not found, we return a 404 error.
    """
    task = db.query(Task).filter(Task.id == task_id).first()   # SELECT * FROM tasks WHERE id = ?
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ============================================================
# UPDATE — PUT /api/tasks/{task_id}
# ============================================================
@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task — edit description, change priority, or mark complete.

    Only updates the fields that were sent in the request body.
    TaskUpdate has all optional fields, so you can send just {"completed": true}
    and it won't touch description or priority.

    When marking a task as completed, we also record completed_at timestamp.
    When un-completing a task, we clear completed_at back to null.
    """
    # Find the task to update
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Only update fields that were provided (not None)
    if task_update.description is not None:
        task.description = task_update.description

    if task_update.priority is not None:
        task.priority = task_update.priority

    if task_update.completed is not None:
        task.completed = task_update.completed
        # If marking as completed, record the timestamp
        if task_update.completed:
            from datetime import datetime
            task.completed_at = datetime.utcnow()
        else:
            # If un-completing, clear the timestamp
            task.completed_at = None

    db.commit()         # Save changes to database
    db.refresh(task)    # Reload to get updated values
    return task


# ============================================================
# DELETE — DELETE /api/tasks/{task_id}
# ============================================================
@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a task.

    This is irreversible — the task is removed from the database.
    The command parser flags "delete task" with needs_confirm=True,
    so the user sees a confirmation dialog before this runs.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)   # Stage the deletion
    db.commit()       # Execute the deletion
    return {"message": f"Task {task_id} deleted"}
