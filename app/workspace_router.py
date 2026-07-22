from fastapi import APIRouter, Depends, status

from app.api_docs import auth_responses, owner_responses
from app.dependencies import get_current_user, get_workspace_service
from app.schemas import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED, responses=auth_responses)
def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user=Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    return service.create_workspace(workspace_data, current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceResponse, responses=owner_responses)
def get_workspace(
    workspace_id: int,
    current_user=Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    return service.get_workspace(workspace_id, current_user.id, current_user.role)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse, responses=owner_responses)
def update_workspace(
    workspace_id: int,
    workspace_data: WorkspaceUpdate,
    current_user=Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    return service.update_workspace(workspace_id, workspace_data, current_user.id, current_user.role)


@router.delete("/{workspace_id}", responses=owner_responses)
def delete_workspace(
    workspace_id: int,
    current_user=Depends(get_current_user),
    service: WorkspaceService = Depends(get_workspace_service),
):
    return service.delete_workspace(workspace_id, current_user.id, current_user.role)
