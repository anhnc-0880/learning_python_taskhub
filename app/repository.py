from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_project(self, project_id: int) -> List[Task]:
        return self._db.query(Task).filter(Task.project_id == project_id).all()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._db.query(Task).filter(Task.id == task_id).first()

    def create(self, project_id: int, task_data: dict, created_by: int) -> Task:
        new_task = Task(
            project_id=project_id,
            created_by=created_by,
            **task_data,
        )
        self._db.add(new_task)
        self._db.commit()
        self._db.refresh(new_task)
        return new_task

    def update(self, task_id: int, task_data: dict) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if task is None:
            return None

        for key, value in task_data.items():
            setattr(task, key, value)

        self._db.commit()
        self._db.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if task is None:
            return False

        self._db.delete(task)
        self._db.commit()
        return True
