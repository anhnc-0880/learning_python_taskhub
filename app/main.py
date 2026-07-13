from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Chay khi startup
    print("TaskHub API startup...")
    yield
    # Chay khi shutdown
    print("TaskHub API shutdown...")

app = FastAPI(
    title="TaskHub API",
    lifespan=lifespan
)

@app.get("/")
def home():
    return {"message": "Welcome to TaskHub API", "docs": "/docs"}

app.include_router(router, prefix="/api/v1")
