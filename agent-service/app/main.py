from fastapi import FastAPI
from app.api.endpoints import users

app = FastAPI(title="Agent Service")

app.include_router(users.router, prefix="/api/v1")

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
