from fastapi import HTTPException, status

from app.models import Workspace
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository


class WorkspacePermissionService:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        member_repo: WorkspaceMemberRepository,
    ):
        self._workspace_repo = workspace_repo
        self._member_repo = member_repo

    def get_member_role(self, workspace_id: int, current_user_id: int, current_user_role: str) -> str:
        if current_user_role == "ADMIN":
            return "OWNER"

        workspace = self._get_workspace_or_404(workspace_id)
        if workspace.owner_id == current_user_id:
            return "OWNER"

        member = self._member_repo.get_member(workspace_id, current_user_id)
        if member is not None:
            return member.role

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    def check_member(self, workspace_id: int, current_user_id: int, current_user_role: str) -> str:
        return self.get_member_role(workspace_id, current_user_id, current_user_role)

    def check_editor(self, workspace_id: int, current_user_id: int, current_user_role: str, detail: str) -> None:
        role = self.get_member_role(workspace_id, current_user_id, current_user_role)
        if role in ["OWNER", "EDITOR"]:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

    def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return workspace
