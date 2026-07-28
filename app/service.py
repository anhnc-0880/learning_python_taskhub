from typing import Any, List, Optional
from fastapi import BackgroundTasks, HTTPException, status
from app.auth_repository import UserRepository
from app.cache import CacheService
from app.notification_service import send_task_assigned_notification
from app.permission_service import WorkspacePermissionService
from app.project_repository import ProjectRepository
from app.repository import TaskRepository
from app.models import Project, Task, User
from app.schemas import TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from app.workspace_member_repository import WorkspaceMemberRepository

class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        member_repo: WorkspaceMemberRepository,
        user_repo: UserRepository,
        cache_service: CacheService,
        permission_service: WorkspacePermissionService,
    ):
        self._task_repo = task_repo
        self._project_repo = project_repo
        self._member_repo = member_repo
        self._user_repo = user_repo
        self._cache_service = cache_service
        self._permission_service = permission_service

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
    ) -> List[Any]:
        project = self._get_project_or_404(project_id)
        self._permission_service.check_member(project.workspace_id, current_user_id, current_user_role)

        cache_key = self._get_tasks_cache_key(project_id, status_filter, priority, assignee_id, page, limit)
        cached_tasks = self._cache_service.get(cache_key)
        if cached_tasks is not None:
            return cached_tasks

        tasks = self._task_repo.get_by_project(
            project_id=project_id,
            status_filter=status_filter,
            priority=priority,
            assignee_id=assignee_id,
            page=page,
            limit=limit,
        )
        self._cache_service.set(cache_key, [self._task_to_dict(task) for task in tasks])
        return tasks

    def create_task(
        self,
        project_id: int,
        task_data: TaskCreate,
        created_by: int,
        current_user_role: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Task:
        project = self._get_project_or_404(project_id)
        self._check_workspace_editor(project.workspace_id, created_by, current_user_role)

        task_dict = task_data.model_dump()
        assignee = self._check_assignee(project, task_dict.get("assignee_id"))
        task = self._task_repo.create(project_id, task_dict, created_by)
        self._clear_tasks_cache(project.id)

        if background_tasks is not None and assignee is not None:
            background_tasks.add_task(send_task_assigned_notification, task, assignee)

        return task

    def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
        current_user_id: int,
        current_user_role: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> Task:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        project = self._get_project_or_404(task.project_id)
        self._check_workspace_editor(project.workspace_id, current_user_id, current_user_role)

        update_dict = task_data.model_dump(exclude_unset=True)
        assignee = None
        if "assignee_id" in update_dict:
            assignee = self._check_assignee(project, update_dict["assignee_id"])

        updated_task = self._task_repo.update(task_id, update_dict)
        self._clear_tasks_cache(project.id)

        if background_tasks is not None and assignee is not None:
            background_tasks.add_task(send_task_assigned_notification, updated_task, assignee)

        return updated_task

    def delete_task(self, task_id: int, current_user_id: int, current_user_role: str) -> dict:
        task = self._task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        project = self._get_project_or_404(task.project_id)
        self._check_workspace_editor(project.workspace_id, current_user_id, current_user_role)

        self._task_repo.delete(task_id)
        self._clear_tasks_cache(project.id)
        return {"message": "Task deleted"}

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self._project_repo.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        return project

    def _check_workspace_editor(self, workspace_id: int, current_user_id: int, current_user_role: str) -> None:
        self._permission_service.check_editor(
            workspace_id,
            current_user_id,
            current_user_role,
            "Only owner or editor can manage tasks",
        )

    def _check_assignee(self, project: Project, assignee_id: Optional[int]) -> Optional[User]:
        if assignee_id is None:
            return None

        assignee = self._user_repo.get_by_id(assignee_id)
        if assignee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found",
            )

        member = self._member_repo.get_member(project.workspace_id, assignee_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a workspace member",
            )
        return assignee

    def _get_tasks_cache_key(
        self,
        project_id: int,
        status_filter: Optional[TaskStatus],
        priority: Optional[TaskPriority],
        assignee_id: Optional[int],
        page: int,
        limit: int,
    ) -> str:
        status_value = status_filter.value if status_filter else "all"
        priority_value = priority.value if priority else "all"
        assignee_value = assignee_id if assignee_id is not None else "all"
        return f"project_tasks:{project_id}:{status_value}:{priority_value}:{assignee_value}:{page}:{limit}"

    def _clear_tasks_cache(self, project_id: int) -> None:
        self._cache_service.delete_by_prefix(f"project_tasks:{project_id}:")

    def _task_to_dict(self, task: Task) -> dict:
        return {
            "id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "assignee_id": task.assignee_id,
            "created_by": task.created_by,
            "created_at": task.created_at,
        }
