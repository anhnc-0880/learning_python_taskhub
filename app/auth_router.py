from fastapi import APIRouter, Depends, status

from app.api_docs import auth_responses, public_responses
from app.auth_service import AuthService
from app.dependencies import get_auth_service, get_current_user
from app.schemas import LogoutRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=public_responses,
)
def register(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return service.register(user_data)


@router.post("/login", response_model=TokenResponse, responses=public_responses)
def login(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return service.login(credentials)


@router.post("/refresh", response_model=TokenResponse, responses=public_responses)
def refresh(
    token_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.refresh(token_data)


@router.post("/logout", responses=auth_responses)
def logout(
    token_data: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.logout(token_data)


@router.get("/me", response_model=UserResponse, responses=auth_responses)
def me(current_user=Depends(get_current_user)):
    return current_user
