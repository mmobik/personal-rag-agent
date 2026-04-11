from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import users, chat, ui
from app.api.endpoints.admin_chat_history import router as admin_chat_history_router
from app.api.endpoints.auth import router as auth_router
from app.db import engine, Base
from app.db import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: выполняется при запуске
    print("Starting Agent Service...")
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created")
    yield
    # Shutdown: выполняется при остановке
    print("Shutting down Agent Service...")

# Используем lifespan вместо on_event
app = FastAPI(
    title="Agent Service",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin_chat_history_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ui.router)

@app.get("/")
async def read_root():
    return {
        "name": "Agent Service",
        "role": "Управление агентами и их состоянием",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "agent-service"}