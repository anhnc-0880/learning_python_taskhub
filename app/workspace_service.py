from fastapi import HTTPException, status

from app.auth_repository import UserRepository
from app.models import Workspace, WorkspaceMember
from app.schemas import WorkspaceCreate, WorkspaceMemberCreate, WorkspaceMemberUpdate, WorkspaceUpdate
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository


class WorkspaceService:
    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        member_repo: WorkspaceMemberRepository,
        user_repo: UserRepository,
    ):
        self._workspace_repo = workspace_repo
        self._member_repo = member_repo
        self._user_repo = user_repo

    def create_workspace(self, workspace_data: WorkspaceCreate, owner_id: int) -> Workspace:
        data = workspace_data.model_dump()
        data["name"] = data["name"].strip()
        workspace = self._workspace_repo.create(data, owner_id)
        self._member_repo.create(workspace.id, owner_id, "OWNER")
        return workspace

    def get_workspace(self, workspace_id: int, current_user_id: int, current_user_role: str) -> Workspace:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_member(workspace.id, current_user_id, current_user_role)
        return workspace

    def update_workspace(
        self,
        workspace_id: int,
        workspace_data: WorkspaceUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Workspace:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace.id, current_user_id, current_user_role)

        update_data = workspace_data.model_dump(exclude_unset=True)
        if "name" in update_data:
            update_data["name"] = update_data["name"].strip()

        return self._workspace_repo.update(workspace, update_data)

    def delete_workspace(self, workspace_id: int, current_user_id: int, current_user_role: str) -> dict:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace.id, current_user_id, current_user_role)
        self._workspace_repo.delete(workspace)
        return {"message": "Workspace deleted"}

    def list_members(self, workspace_id: int, current_user_id: int, current_user_role: str) -> list[WorkspaceMember]:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_member(workspace.id, current_user_id, current_user_role)
        return self._member_repo.get_by_workspace(workspace.id)

    def invite_member(
        self,
        workspace_id: int,
        member_data: WorkspaceMemberCreate,
        current_user_id: int,
        current_user_role: str,
    ) -> WorkspaceMember:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace.id, current_user_id, current_user_role)

        user = self._user_repo.get_by_id(member_data.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        member = self._member_repo.get_member(workspace.id, member_data.user_id)
        if member is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already in workspace",
            )

        return self._member_repo.create(workspace.id, member_data.user_id, member_data.role.value)

    def update_member(
        self,
        workspace_id: int,
        user_id: int,
        member_data: WorkspaceMemberUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> WorkspaceMember:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace.id, current_user_id, current_user_role)

        member = self._get_member_or_404(workspace.id, user_id)
        if member.role == "OWNER":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change workspace owner role",
            )

        return self._member_repo.update(member, member_data.role.value)

    def remove_member(
        self,
        workspace_id: int,
        user_id: int,
        current_user_id: int,
        current_user_role: str,
    ) -> dict:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_owner(workspace.id, current_user_id, current_user_role)

        member = self._get_member_or_404(workspace.id, user_id)
        if member.role == "OWNER":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove workspace owner",
            )

        self._member_repo.delete(member)
        return {"message": "Member removed"}

    def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return workspace

    def _get_member_or_404(self, workspace_id: int, user_id: int) -> WorkspaceMember:
        member = self._member_repo.get_member(workspace_id, user_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace member not found",
            )
        return member

    def _check_member(self, workspace_id: int, current_user_id: int, current_user_role: str) -> WorkspaceMember:
        if current_user_role == "ADMIN":
            return WorkspaceMember(workspace_id=workspace_id, user_id=current_user_id, role="OWNER")

        workspace = self._get_workspace_or_404(workspace_id)
        if workspace.owner_id == current_user_id:
            return WorkspaceMember(workspace_id=workspace_id, user_id=current_user_id, role="OWNER")

        member = self._member_repo.get_member(workspace_id, current_user_id)
        if member is not None:
            return member

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    def _check_owner(self, workspace_id: int, current_user_id: int, current_user_role: str) -> WorkspaceMember:
        member = self._check_member(workspace_id, current_user_id, current_user_role)
        if current_user_role == "ADMIN" or member.role == "OWNER":
            return member

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can manage this workspace",
        )
