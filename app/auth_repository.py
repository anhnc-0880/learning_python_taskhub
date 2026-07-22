from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import RefreshToken, User


class UserRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self._db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._db.query(User).filter(User.id == user_id).first()

    def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update(self, user: User, user_data: dict) -> User:
        for key, value in user_data.items():
            setattr(user, key, value)

        self._db.commit()
        self._db.refresh(user)
        return user

    def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )
        self._db.add(refresh_token)
        self._db.commit()
        self._db.refresh(refresh_token)
        return refresh_token

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return self._db.query(RefreshToken).filter(RefreshToken.token == token).first()

    def revoke_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.revoked = True
        self._db.commit()
        self._db.refresh(refresh_token)
        return refresh_token
