from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth_repository import UserRepository
from app.auth_service import AuthService
from app.comment_repository import CommentRepository
from app.comment_service import CommentService
from app.label_repository import LabelRepository
from app.label_service import LabelService
from app.database import SessionLocal
from app.project_repository import ProjectRepository
from app.project_service import ProjectService
from app.repository import TaskRepository
from app.models import User
from app.security import decode_access_token
from app.service import TaskService
from app.workspace_member_repository import WorkspaceMemberRepository
from app.workspace_repository import WorkspaceRepository
from app.workspace_service import WorkspaceService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo)


def get_workspace_repo(db: Session = Depends(get_db)) -> WorkspaceRepository:
    return WorkspaceRepository(db)


def get_workspace_member_repo(db: Session = Depends(get_db)) -> WorkspaceMemberRepository:
    return WorkspaceMemberRepository(db)


def get_workspace_service(
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    member_repo: WorkspaceMemberRepository = Depends(get_workspace_member_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> WorkspaceService:
    return WorkspaceService(workspace_repo, member_repo, user_repo)


def get_project_repo(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    member_repo: WorkspaceMemberRepository = Depends(get_workspace_member_repo),
) -> ProjectService:
    return ProjectService(project_repo, workspace_repo, member_repo)


def get_task_repo(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_label_repo(db: Session = Depends(get_db)) -> LabelRepository:
    return LabelRepository(db)


def get_comment_repo(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    member_repo: WorkspaceMemberRepository = Depends(get_workspace_member_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> TaskService:
    return TaskService(task_repo, project_repo, workspace_repo, member_repo, user_repo)


def get_label_service(
    label_repo: LabelRepository = Depends(get_label_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    member_repo: WorkspaceMemberRepository = Depends(get_workspace_member_repo),
) -> LabelService:
    return LabelService(label_repo, project_repo, task_repo, workspace_repo, member_repo)


def get_comment_service(
    comment_repo: CommentRepository = Depends(get_comment_repo),
    task_repo: TaskRepository = Depends(get_task_repo),
    project_repo: ProjectRepository = Depends(get_project_repo),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repo),
    member_repo: WorkspaceMemberRepository = Depends(get_workspace_member_repo),
) -> CommentService:
    return CommentService(comment_repo, task_repo, project_repo, workspace_repo, member_repo)


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
