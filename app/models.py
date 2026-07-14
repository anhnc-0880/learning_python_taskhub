from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="TODO")
    priority = Column(String(20), nullable=False, default="MEDIUM")
    due_date = Column(Date, nullable=True)
    assignee_id = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

