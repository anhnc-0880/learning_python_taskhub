from typing import Optional

from sqlalchemy.orm import Session

from app.models import User


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
