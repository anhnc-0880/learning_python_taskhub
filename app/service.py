from typing import List
from fastapi import HTTPException, status
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self._task_repo = task_repo

    def get_tasks_by_project(self, project_id: int) -> List[dict]:
        # Fake project tu 1 den 5
        if project_id < 1 or project_id > 5:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return self._task_repo.get_by_project(project_id)

    def create_task(self, project_id: int, task_data: TaskCreate, created_by: int) -> dict:
        if project_id < 1 or project_id > 5:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return self._task_repo.create(project_id, task_data.model_dump(), created_by)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> dict:
        update_dict = task_data.model_dump(exclude_unset=True)
        updated_task = self._task_repo.update(task_id, update_dict)
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return updated_task

    def delete_task(self, task_id: int) -> dict:
        success = self._task_repo.delete(task_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return {"message": "Task deleted"}
