from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.service import TaskService
from app.dependencies import get_task_service, get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
def get_project_tasks(
    project_id: int,
    service: TaskService = Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    return service.get_tasks_by_project(project_id)

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int, 
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    return service.create_task(project_id, task_data, current_user.id)

@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    return service.update_task(task_id, task_data, current_user.id, current_user.role)

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user=Depends(get_current_user),
):
    return service.delete_task(task_id, current_user.id, current_user.role)
