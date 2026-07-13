from fastapi import Depends
from app.repository import TaskRepository
from app.service import TaskService

# Repository luu trong RAM nen can dung chung 1 instance (Singleton)
_task_repo = TaskRepository()

def get_task_repo() -> TaskRepository:
    return _task_repo

def get_task_service(repo: TaskRepository = Depends(get_task_repo)) -> TaskService:
    return TaskService(repo)

def get_current_user_id() -> int:
    # Fake user_id = 1 khi chua lam JWT auth ở Day 3
    return 1
