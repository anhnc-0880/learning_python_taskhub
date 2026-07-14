from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    DONE = "DONE"

class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TaskBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    project_id: int
    created_by: int
    created_at: datetime
