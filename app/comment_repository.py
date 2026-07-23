from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Comment


class CommentRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, task_id: int, author_id: int, comment_data: dict) -> Comment:
        comment = Comment(task_id=task_id, author_id=author_id, **comment_data)
        self._db.add(comment)
        self._db.commit()
        self._db.refresh(comment)
        return comment

    def get_by_task(self, task_id: int) -> List[Comment]:
        return self._db.query(Comment).filter(Comment.task_id == task_id).all()

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        return self._db.query(Comment).filter(Comment.id == comment_id).first()

    def delete(self, comment: Comment) -> None:
        self._db.delete(comment)
        self._db.commit()
