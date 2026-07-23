from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import WorkspaceMember


class WorkspaceMemberRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, workspace_id: int, user_id: int, role: str) -> WorkspaceMember:
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        self._db.add(member)
        self._db.commit()
        self._db.refresh(member)
        return member

    def get_by_workspace(self, workspace_id: int) -> List[WorkspaceMember]:
        return self._db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()

    def get_member(self, workspace_id: int, user_id: int) -> Optional[WorkspaceMember]:
        return (
            self._db.query(WorkspaceMember)
            .filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == user_id)
            .first()
        )

    def update(self, member: WorkspaceMember, role: str) -> WorkspaceMember:
        member.role = role
        self._db.commit()
        self._db.refresh(member)
        return member

    def delete(self, member: WorkspaceMember) -> None:
        self._db.delete(member)
        self._db.commit()
