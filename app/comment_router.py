from typing import List

from fastapi import APIRouter, Depends, status

from app.api_docs import auth_responses, owner_responses
from app.comment_service import CommentService
from app.dependencies import get_comment_service, get_current_user
from app.schemas import CommentCreate, CommentResponse

router = APIRouter(tags=["Comments"])


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=auth_responses,
)
def create_comment(
    task_id: int,
    comment_data: CommentCreate,
    current_user=Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return service.create_comment(task_id, comment_data, current_user.id, current_user.role)


@router.get("/tasks/{task_id}/comments", response_model=List[CommentResponse], responses=auth_responses)
def list_comments(
    task_id: int,
    current_user=Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return service.list_comments(task_id, current_user.id, current_user.role)


@router.delete("/comments/{comment_id}", responses=owner_responses)
def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_user),
    service: CommentService = Depends(get_comment_service),
):
    return service.delete_comment(comment_id, current_user.id, current_user.role)
