from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
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


class ProjectStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class WorkspaceMemberRole(str, Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"


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


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    email: str = Field(..., min_length=3)
    full_name: str = Field(..., min_length=1)


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3)
    full_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, min_length=3)
    full_name: Optional[str] = Field(None, min_length=1)


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class ErrorResponse(BaseModel):
    message: str
    request_id: Optional[str] = None


class ValidationErrorResponse(ErrorResponse):
    errors: list[dict[str, Any]]


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1)


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    workspace_id: int
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime


class WorkspaceMemberCreate(BaseModel):
    user_id: int
    role: WorkspaceMemberRole = WorkspaceMemberRole.VIEWER


class WorkspaceMemberUpdate(BaseModel):
    role: WorkspaceMemberRole


class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceMemberRole
    created_at: datetime


class LabelCreate(BaseModel):
    name: str = Field(..., min_length=1)
    color: str = Field(..., min_length=1)


class LabelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    color: Optional[str] = Field(None, min_length=1)


class LabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    color: str
    created_at: datetime


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    content: str
    created_at: datetime
