from typing import List

from fastapi import HTTPException, status

from app.label_repository import LabelRepository
from app.models import Label, Project, Task
from app.project_repository import ProjectRepository
from app.repository import TaskRepository
from app.schemas import LabelCreate, LabelUpdate
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository


class LabelService:
    def __init__(
        self,
        label_repo: LabelRepository,
        project_repo: ProjectRepository,
        task_repo: TaskRepository,
        workspace_repo: WorkspaceRepository,
        member_repo: WorkspaceMemberRepository,
    ):
        self._label_repo = label_repo
        self._project_repo = project_repo
        self._task_repo = task_repo
        self._workspace_repo = workspace_repo
        self._member_repo = member_repo

    def create_label(
        self,
        project_id: int,
        label_data: LabelCreate,
        current_user_id: int,
        current_user_role: str,
    ) -> Label:
        project = self._get_project_or_404(project_id)
        self._check_editor(project, current_user_id, current_user_role)

        data = label_data.model_dump()
        data["name"] = data["name"].strip()
        data["color"] = data["color"].strip()
        return self._label_repo.create(project.id, data)

    def list_labels(self, project_id: int, current_user_id: int, current_user_role: str) -> List[Label]:
        project = self._get_project_or_404(project_id)
        self._check_member(project, current_user_id, current_user_role)
        return self._label_repo.get_by_project(project.id)

    def update_label(
        self,
        label_id: int,
        label_data: LabelUpdate,
        current_user_id: int,
        current_user_role: str,
    ) -> Label:
        label = self._get_label_or_404(label_id)
        project = self._get_project_or_404(label.project_id)
        self._check_editor(project, current_user_id, current_user_role)

        data = label_data.model_dump(exclude_unset=True)
        if "name" in data:
            data["name"] = data["name"].strip()
        if "color" in data:
            data["color"] = data["color"].strip()

        return self._label_repo.update(label, data)

    def delete_label(self, label_id: int, current_user_id: int, current_user_role: str) -> dict:
        label = self._get_label_or_404(label_id)
        project = self._get_project_or_404(label.project_id)
        self._check_editor(project, current_user_id, current_user_role)
        self._label_repo.delete(label)
        return {"message": "Label deleted"}

    def add_label_to_task(
        self,
        task_id: int,
        label_id: int,
        current_user_id: int,
        current_user_role: str,
    ) -> dict:
        task = self._get_task_or_404(task_id)
        label = self._get_label_or_404(label_id)
        project = self._get_project_or_404(task.project_id)
        self._check_editor(project, current_user_id, current_user_role)

        if label.project_id != project.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Label does not belong to this project",
            )

        task_label = self._label_repo.get_task_label(task.id, label.id)
        if task_label is None:
            self._label_repo.add_to_task(task.id, label.id)

        return {"message": "Label added to task"}

    def remove_label_from_task(
        self,
        task_id: int,
        label_id: int,
        current_user_id: int,
        current_user_role: str,
    ) -> dict:
        task = self._get_task_or_404(task_id)
        project = self._get_project_or_404(task.project_id)
        self._check_editor(project, current_user_id, current_user_role)

        task_label = self._label_repo.get_task_label(task.id, label_id)
        if task_label is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task label not found",
            )

        self._label_repo.remove_from_task(task_label)
        return {"message": "Label removed from task"}

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def _get_label_or_404(self, label_id: int) -> Label:
        label = self._label_repo.get_by_id(label_id)
        if label is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Label not found",
            )
        return label

    def _get_task_or_404(self, task_id: int) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    def _check_member(self, project: Project, current_user_id: int, current_user_role: str) -> str:
        if current_user_role == "ADMIN":
            return "OWNER"

        workspace = self._workspace_repo.get_by_id(project.workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )

        if workspace.owner_id == current_user_id:
            return "OWNER"

        member = self._member_repo.get_member(workspace.id, current_user_id)
        if member is not None:
            return member.role

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    def _check_editor(self, project: Project, current_user_id: int, current_user_role: str) -> None:
        role = self._check_member(project, current_user_id, current_user_role)
        if role in ["OWNER", "EDITOR"]:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or editor can manage labels",
        )
