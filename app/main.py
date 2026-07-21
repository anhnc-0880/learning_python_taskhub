from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from app.auth_router import router as auth_router
from app.config import settings
from app.exception_handlers import setup_exception_handlers
from app.database import Base, SessionLocal, engine
from app.logging_config import setup_logging
from app.models import Task
from app.middleware import setup_middleware
from app.repository import TaskRepository
from app.router import router
from app.user_router import router as user_router

setup_logging()
logger = logging.getLogger("taskhub")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(Task).count() == 0:
            task_repo = TaskRepository(db)
            task_repo.create(
                project_id=1,
                task_data={
                    "title": "Setup skeleton app",
                    "description": "Tao project setup layered architecture",
                    "status": "DONE",
                    "priority": "HIGH",
                    "due_date": None,
                    "assignee_id": 1,
                },
                created_by=1,
            )
    finally:
        db.close()

    logger.info("TaskHub API startup")
    yield
    logger.info("TaskHub API shutdown")

app = FastAPI(
    title=settings.app_name,
    description="TaskHub API for learning FastAPI with auth, tasks, middleware, and configuration.",
    version="0.1.0",
    lifespan=lifespan
)

setup_middleware(app)
setup_exception_handlers(app)

@app.get("/")
def home():
    return {"message": "Welcome to TaskHub API", "docs": "/docs"}

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
