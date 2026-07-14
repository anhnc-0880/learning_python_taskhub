from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repository import TaskRepository
from app.service import TaskService


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_task_repo(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)

def get_task_service(repo: TaskRepository = Depends(get_task_repo)) -> TaskService:
    return TaskService(repo)

def get_current_user_id() -> int:
    # Fake user_id = 1 khi chua lam JWT auth ở Day 3
    return 1
