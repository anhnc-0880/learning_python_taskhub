from fastapi import HTTPException, status

from app.models import Workspace
from app.schemas import WorkspaceCreate, WorkspaceUpdate
from app.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(self, workspace_repo: WorkspaceRepository):
        self._workspace_repo = workspace_repo

    def create_workspace(self, workspace_data: WorkspaceCreate, owner_id: int) -> Workspace:
        data = workspace_data.model_dump()
        data["name"] = data["name"].strip()
        return self._workspace_repo.create(data, owner_id)

    def get_workspace(self, workspace_id: int, current_user_id: int, current_user_role: str) -> Workspace:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace, current_user_id, current_user_role)
        return workspace

    def update_workspace(
        self,
        workspace_id: int,
        workspace_data: WorkspaceUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Workspace:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace, current_user_id, current_user_role)

        update_data = workspace_data.model_dump(exclude_unset=True)
        if "name" in update_data:
            update_data["name"] = update_data["name"].strip()

        return self._workspace_repo.update(workspace, update_data)

    def delete_workspace(self, workspace_id: int, current_user_id: int, current_user_role: str) -> dict:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace, current_user_id, current_user_role)
        self._workspace_repo.delete(workspace)
        return {"message": "Workspace deleted"}

    def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return workspace

    def _check_owner(self, workspace: Workspace, current_user_id: int, current_user_role: str) -> None:
        if current_user_role == "ADMIN" or workspace.owner_id == current_user_id:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can manage this workspace",
        )
