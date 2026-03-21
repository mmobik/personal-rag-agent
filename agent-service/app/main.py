from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import users, chat, ui
from app.api.endpoints.admin_chat_history import router as admin_chat_history_router

app = FastAPI(title="Agent Service")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin_chat_history_router, prefix="/api/v1")
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
