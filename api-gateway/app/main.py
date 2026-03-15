from fastapi import FastAPI
from app.api.endpoints import health, users, chat

app = FastAPI()

app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {
        "name": "API Gateway",
        "role": "Маршрутизатор запросов к agent-service, rag-service и другим микросервисам",
        "status": "running",
        "docs": "/docs"
    }