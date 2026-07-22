from typing import Optional

from sqlalchemy.orm import Session

from app.models import Workspace


class WorkspaceRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, workspace_data: dict, owner_id: int) -> Workspace:
        workspace = Workspace(owner_id=owner_id, **workspace_data)
        self._db.add(workspace)
        self._db.commit()
        self._db.refresh(workspace)
        return workspace

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        return self._db.query(Workspace).filter(Workspace.id == workspace_id).first()

    def update(self, workspace: Workspace, workspace_data: dict) -> Workspace:
        for key, value in workspace_data.items():
            setattr(workspace, key, value)

        self._db.commit()
        self._db.refresh(workspace)
        return workspace

    def delete(self, workspace: Workspace) -> None:
        self._db.delete(workspace)
        self._db.commit()
