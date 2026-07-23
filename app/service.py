from typing import List, Optional
from fastapi import HTTPException, status
from app.auth_repository import UserRepository
from app.project_repository import ProjectRepository
from app.repository import TaskRepository
from app.models import Project, Task, Workspace
from app.schemas import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository

class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        workspace_repo: WorkspaceRepository,
        member_repo: WorkspaceMemberRepository,
        user_repo: UserRepository,
    ):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._workspace_repo = workspace_repo
        self._member_repo = member_repo
        self._user_repo = user_repo

    def get_tasks_by_project(
        self,
        project_id: int,
        status_filter: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee_id: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
        current_user_id: int = 0,
        current_user_role: str = "MEMBER",
    ) -> List[Task]:
        project = self._get_project_or_404(project_id)
        self._check_workspace_member(project, current_user_id, current_user_role)
        return self._task_repo.get_by_project(
            project_id=project_id,
            status_filter=status_filter,
            priority=priority,
            assignee_id=assignee_id,
            page=page,
            limit=limit,
        )

    def create_task(
        self,
        project_id: int,
        task_data: TaskCreate,
        created_by: int,
        current_user_role: str,
    ) -> Task:
        project = self._get_project_or_404(project_id)
        self._check_workspace_editor(project, created_by, current_user_role)

        task_dict = task_data.model_dump()
        self._check_assignee(project, task_dict.get("assignee_id"))
        return self._task_repo.create(project_id, task_dict, created_by)

    def update_task(self, task_id: int, task_data: TaskUpdate, current_user_id: int, current_user_role: str) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        project = self._get_project_or_404(task.project_id)
        self._check_workspace_editor(project, current_user_id, current_user_role)

        update_dict = task_data.model_dump(exclude_unset=True)
        if "assignee_id" in update_dict:
            self._check_assignee(project, update_dict["assignee_id"])
        return self._task_repo.update(task_id, update_dict)

    def delete_task(self, task_id: int, current_user_id: int, current_user_role: str) -> dict:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        project = self._get_project_or_404(task.project_id)
        self._check_workspace_editor(project, current_user_id, current_user_role)

        self._task_repo.delete(task_id)
        return {"message": "Task deleted"}

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project

    def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        workspace = self._workspace_repo.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        return workspace

    def _check_workspace_member(self, project: Project, current_user_id: int, current_user_role: str) -> str:
        workspace = self._get_workspace_or_404(project.workspace_id)
        if current_user_role == "ADMIN":
            return "OWNER"

        if workspace.owner_id == current_user_id:
            return "OWNER"

        member = self._member_repo.get_member(workspace.id, current_user_id)
        if member is not None:
            return member.role

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )

    def _check_workspace_editor(self, project: Project, current_user_id: int, current_user_role: str) -> None:
        role = self._check_workspace_member(project, current_user_id, current_user_role)
        if role in ["OWNER", "EDITOR"]:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or editor can manage tasks"
        )

    def _check_assignee(self, project: Project, assignee_id: Optional[int]) -> None:
        if assignee_id is None:
            return

        assignee = self._user_repo.get_by_id(assignee_id)
        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )

        member = self._member_repo.get_member(project.workspace_id, assignee_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a workspace member"
            )
