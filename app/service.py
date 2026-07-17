from typing import List
from fastapi import HTTPException, status
from app.repository import TaskRepository
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self._task_repo = task_repo

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        if project_id < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return self._task_repo.get_by_project(project_id)

    def create_task(self, project_id: int, task_data: TaskCreate, created_by: int) -> Task:
        if project_id < 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return self._task_repo.create(project_id, task_data.model_dump(), created_by)

    def _can_manage_task(self, task: Task, current_user_id: int, current_user_role: str) -> bool:
        return current_user_role == "ADMIN" or task.created_by == current_user_id

    def update_task(self, task_id: int, task_data: TaskUpdate, current_user_id: int, current_user_role: str) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if not self._can_manage_task(task, current_user_id, current_user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot edit this task"
            )

        update_dict = task_data.model_dump(exclude_unset=True)
        return self._task_repo.update(task_id, update_dict)

    def delete_task(self, task_id: int, current_user_id: int, current_user_role: str) -> dict:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        if not self._can_manage_task(task, current_user_id, current_user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete this task"
            )

        self._task_repo.delete(task_id)
        return {"message": "Task deleted"}
