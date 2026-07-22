from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, workspace_id: int, project_data: dict) -> Project:
        project = Project(workspace_id=workspace_id, **project_data)
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project

    def get_by_workspace(self, workspace_id: int) -> List[Project]:
        return self._db.query(Project).filter(Project.workspace_id == workspace_id).all()

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self._db.query(Project).filter(Project.id == project_id).first()

    def update(self, project: Project, project_data: dict) -> Project:
        for key, value in project_data.items():
            setattr(project, key, value)

        self._db.commit()
        self._db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self._db.delete(project)
        self._db.commit()
