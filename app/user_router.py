from fastapi import APIRouter, Depends

from app.api_docs import auth_responses
from app.auth_service import AuthService
from app.dependencies import get_auth_service, get_current_user
from app.schemas import ChangePassword, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, responses=auth_responses)
def get_profile(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse, responses=auth_responses)
def update_profile(
    user_data: UserUpdate,
    current_user=Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return service.update_profile(current_user, user_data)


@router.post("/me/change-password", responses=auth_responses)
def change_password(
    password_data: ChangePassword,
    current_user=Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return service.change_password(current_user, password_data)
