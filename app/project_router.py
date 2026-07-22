from typing import List

from fastapi import APIRouter, Depends, status

from app.api_docs import auth_responses, owner_responses
from app.dependencies import get_current_user, get_project_service
from app.project_service import ProjectService
from app.schemas import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(tags=["Projects"])


@router.post(
    "/workspaces/{workspace_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses=owner_responses,
)
def create_project(
    workspace_id: int,
    project_data: ProjectCreate,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.create_project(workspace_id, project_data, current_user.id, current_user.role)


@router.get("/workspaces/{workspace_id}/projects", response_model=List[ProjectResponse], responses=auth_responses)
def list_projects(
    workspace_id: int,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.list_projects(workspace_id, current_user.id, current_user.role)


@router.get("/projects/{project_id}", response_model=ProjectResponse, responses=owner_responses)
def get_project(
    project_id: int,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.get_project(project_id, current_user.id, current_user.role)


@router.patch("/projects/{project_id}", response_model=ProjectResponse, responses=owner_responses)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.update_project(project_id, project_data, current_user.id, current_user.role)


@router.patch("/projects/{project_id}/archive", response_model=ProjectResponse, responses=owner_responses)
def archive_project(
    project_id: int,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.archive_project(project_id, current_user.id, current_user.role)


@router.delete("/projects/{project_id}", responses=owner_responses)
def delete_project(
    project_id: int,
    current_user=Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.delete_project(project_id, current_user.id, current_user.role)
