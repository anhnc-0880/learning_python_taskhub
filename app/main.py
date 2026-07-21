from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.auth_router import router as auth_router
from app.config import settings
from app.exception_handlers import setup_exception_handlers
from app.database import Base, SessionLocal, engine
from app.models import Task
from app.middleware import setup_middleware
from app.repository import TaskRepository
from app.router import router

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

    print("TaskHub API startup...")
    yield
    print("TaskHub API shutdown...")

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

setup_middleware(app)
setup_exception_handlers(app)

@app.get("/")
def home():
    return {"message": "Welcome to TaskHub API", "docs": "/docs"}

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
