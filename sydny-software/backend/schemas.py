"""
Pydantic Schemas for SYDNY
The bouncer at the door — validates data before it reaches the database.
"""

from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

class TaskCreate(BaseModel):
    """Schema for creating a new task. This is what the frontend sends."""
    description: str
    priority: PriorityEnum = PriorityEnum.normal


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields optional."""
    description: str | None = None
    priority: PriorityEnum | None = None
    completed: bool | None = None

class TaskResponse(BaseModel):
    """Schema for sending task data back to the frontend."""
    id: int
    description: str
    priority: PriorityEnum
    completed: bool
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
