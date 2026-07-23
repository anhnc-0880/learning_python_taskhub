from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Label, TaskLabel


class LabelRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, project_id: int, label_data: dict) -> Label:
        label = Label(project_id=project_id, **label_data)
        self._db.add(label)
        self._db.commit()
        self._db.refresh(label)
        return label

    def get_by_project(self, project_id: int) -> List[Label]:
        return self._db.query(Label).filter(Label.project_id == project_id).all()

    def get_by_id(self, label_id: int) -> Optional[Label]:
        return self._db.query(Label).filter(Label.id == label_id).first()

    def update(self, label: Label, label_data: dict) -> Label:
        for key, value in label_data.items():
            setattr(label, key, value)

        self._db.commit()
        self._db.refresh(label)
        return label

    def delete(self, label: Label) -> None:
        self._db.delete(label)
        self._db.commit()

    def get_task_label(self, task_id: int, label_id: int) -> Optional[TaskLabel]:
        return self._db.query(TaskLabel).filter(TaskLabel.task_id == task_id, TaskLabel.label_id == label_id).first()

    def add_to_task(self, task_id: int, label_id: int) -> TaskLabel:
        task_label = TaskLabel(task_id=task_id, label_id=label_id)
        self._db.add(task_label)
        self._db.commit()
        self._db.refresh(task_label)
        return task_label

    def remove_from_task(self, task_label: TaskLabel) -> None:
        self._db.delete(task_label)
        self._db.commit()
