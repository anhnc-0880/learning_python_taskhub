from fastapi import HTTPException, status

from app.auth_repository import UserRepository
from app.schemas import TokenResponse, UserCreate, UserLogin
from app.security import create_access_token, hash_password, verify_password


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

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role,
            }
        )
        return TokenResponse(access_token=access_token)
