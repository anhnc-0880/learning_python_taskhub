from typing import List

from fastapi import APIRouter, Depends, status

from app.api_docs import auth_responses, owner_responses
from app.dependencies import get_current_user, get_label_service
from app.label_service import LabelService
from app.schemas import LabelCreate, LabelResponse, LabelUpdate

router = APIRouter(tags=["Labels"])


@router.post(
    "/projects/{project_id}/labels",
    response_model=LabelResponse,
    status_code=status.HTTP_201_CREATED,
    responses=owner_responses,
)
def create_label(
    project_id: int,
    label_data: LabelCreate,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.create_label(project_id, label_data, current_user.id, current_user.role)


@router.get("/projects/{project_id}/labels", response_model=List[LabelResponse], responses=auth_responses)
def list_labels(
    project_id: int,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.list_labels(project_id, current_user.id, current_user.role)


@router.patch("/labels/{label_id}", response_model=LabelResponse, responses=owner_responses)
def update_label(
    label_id: int,
    label_data: LabelUpdate,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.update_label(label_id, label_data, current_user.id, current_user.role)


@router.delete("/labels/{label_id}", responses=owner_responses)
def delete_label(
    label_id: int,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.delete_label(label_id, current_user.id, current_user.role)


@router.post("/tasks/{task_id}/labels/{label_id}", responses=owner_responses)
def add_label_to_task(
    task_id: int,
    label_id: int,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.add_label_to_task(task_id, label_id, current_user.id, current_user.role)


@router.delete("/tasks/{task_id}/labels/{label_id}", responses=owner_responses)
def remove_label_from_task(
    task_id: int,
    label_id: int,
    current_user=Depends(get_current_user),
    service: LabelService = Depends(get_label_service),
):
    return service.remove_label_from_task(task_id, label_id, current_user.id, current_user.role)
