from typing import List

from fastapi import HTTPException, status

from app.models import Project, Workspace
from app.project_repository import ProjectRepository
from app.schemas import ProjectCreate, ProjectUpdate
from app.workspace_repository import WorkspaceRepository


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, workspace_repo: WorkspaceRepository):
        self._project_repo = project_repo
        self._workspace_repo = workspace_repo

    def create_project(
        self,
        workspace_id: int,
        project_data: ProjectCreate,
        current_user_id: int,
        current_user_role: str,
    ) -> Project:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_workspace_owner(workspace, current_user_id, current_user_role)

        data = project_data.model_dump()
        data["name"] = data["name"].strip()
        return self._project_repo.create(workspace_id, data)

    def list_projects(self, workspace_id: int, current_user_id: int, current_user_role: str) -> List[Project]:
        workspace = self._get_workspace_or_404(workspace_id)
        self._check_workspace_owner(workspace, current_user_id, current_user_role)
        return self._project_repo.get_by_workspace(workspace_id)

    def get_project(self, project_id: int, current_user_id: int, current_user_role: str) -> Project:
        project = self._get_project_or_404(project_id)
        workspace = self._get_workspace_or_404(project.workspace_id)
        self._check_workspace_owner(workspace, current_user_id, current_user_role)
        return project

    def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Project:
        project = self.get_project(project_id, current_user_id, current_user_role)
        update_data = project_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            update_data["name"] = update_data["name"].strip()

        return self._project_repo.update(project, update_data)

    def archive_project(self, project_id: int, current_user_id: int, current_user_role: str) -> Project:
        project = self.get_project(project_id, current_user_id, current_user_role)
        return self._project_repo.update(project, {"status": "ARCHIVED"})

    def delete_project(self, project_id: int, current_user_id: int, current_user_role: str) -> dict:
        project = self.get_project(project_id, current_user_id, current_user_role)
        self._project_repo.delete(project)
        return {"message": "Project deleted"}

    def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        return workspace

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def _check_workspace_owner(self, workspace: Workspace, current_user_id: int, current_user_role: str) -> None:
        if current_user_role == "ADMIN" or workspace.owner_id == current_user_id:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace owner can manage projects",
        )
