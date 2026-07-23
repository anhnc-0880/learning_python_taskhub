from typing import List

from fastapi import HTTPException, status

from app.comment_repository import CommentRepository
from app.models import Comment, Project, Task
from app.project_repository import ProjectRepository
from app.repository import TaskRepository
from app.schemas import CommentCreate
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        workspace_repo: WorkspaceRepository,
        member_repo: WorkspaceMemberRepository,
    ):
        self._comment_repo = comment_repo
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._workspace_repo = workspace_repo
        self._member_repo = member_repo

    def create_comment(
        self,
        task_id: int,
        comment_data: CommentCreate,
        current_user_id: int,
        current_user_role: str,
    ) -> Comment:
        task = self._get_task_or_404(task_id)
        project = self._get_project_or_404(task.project_id)
        self._check_member(project, current_user_id, current_user_role)

        data = comment_data.model_dump()
        data["content"] = data["content"].strip()
        return self._comment_repo.create(task.id, current_user_id, data)

    def list_comments(self, task_id: int, current_user_id: int, current_user_role: str) -> List[Comment]:
        task = self._get_task_or_404(task_id)
        project = self._get_project_or_404(task.project_id)
        self._check_member(project, current_user_id, current_user_role)
        return self._comment_repo.get_by_task(task.id)

    def delete_comment(self, comment_id: int, current_user_id: int, current_user_role: str) -> dict:
        comment = self._get_comment_or_404(comment_id)
        task = self._get_task_or_404(comment.task_id)
        project = self._get_project_or_404(task.project_id)
        role = self._check_member(project, current_user_id, current_user_role)

        if current_user_role != "ADMIN" and role not in ["OWNER", "EDITOR"] and comment.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete this comment",
            )

        self._comment_repo.delete(comment)
        return {"message": "Comment deleted"}

    def _get_task_or_404(self, task_id: int) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def _get_comment_or_404(self, comment_id: int) -> Comment:
        comment = self._comment_repo.get_by_id(comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        return comment

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
