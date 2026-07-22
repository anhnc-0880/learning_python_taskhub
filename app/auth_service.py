from datetime import datetime, timedelta

from fastapi import HTTPException, status

from app.auth_repository import UserRepository
from app.config import settings
from app.models import User
from app.schemas import ChangePassword, LogoutRequest, RefreshTokenRequest, TokenResponse, UserCreate, UserLogin, UserUpdate
from app.security import create_access_token, create_refresh_token, hash_password, verify_password


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def register(self, user_data: UserCreate):
        email = user_data.email.strip().lower()
        existing_user = self._user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        return self._user_repo.create(
            {
                "email": email,
                "full_name": user_data.full_name.strip(),
                "hashed_password": hash_password(user_data.password),
                "role": "MEMBER",
                "is_active": True,
            }
        )

    def login(self, credentials: UserLogin) -> TokenResponse:
        email = credentials.email.strip().lower()
        user = self._user_repo.get_by_email(email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return self._create_token_response(user)

    def refresh(self, token_data: RefreshTokenRequest) -> TokenResponse:
        refresh_token = self._user_repo.get_refresh_token(token_data.refresh_token)
        if not refresh_token or refresh_token.revoked or refresh_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = self._user_repo.get_by_id(refresh_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        self._user_repo.revoke_refresh_token(refresh_token)
        return self._create_token_response(user)

    def logout(self, token_data: LogoutRequest) -> dict:
        refresh_token = self._user_repo.get_refresh_token(token_data.refresh_token)
        if refresh_token and not refresh_token.revoked:
            self._user_repo.revoke_refresh_token(refresh_token)
        return {"message": "Logged out"}

    def _create_token_response(self, user: User) -> TokenResponse:
        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )
        refresh_token = create_refresh_token()
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        self._user_repo.create_refresh_token(user.id, refresh_token, expires_at)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def update_profile(self, current_user: User, user_data: UserUpdate):
        update_data = user_data.model_dump(exclude_unset=True)

        if "email" in update_data:
            email = update_data["email"].strip().lower()
            existing_user = self._user_repo.get_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )
            update_data["email"] = email

        if "full_name" in update_data:
            update_data["full_name"] = update_data["full_name"].strip()

        return self._user_repo.update(current_user, update_data)

    def change_password(self, current_user: User, password_data: ChangePassword) -> dict:
        if not verify_password(password_data.old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect",
            )

        self._user_repo.update(
            current_user,
            {"hashed_password": hash_password(password_data.new_password)},
        )
        return {"message": "Password changed"}
