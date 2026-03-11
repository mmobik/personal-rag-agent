from fastapi import FastAPI
from app.api.endpoints import health

app = FastAPI()

app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def read_root():
    return {
        "name": "API Gateway",
        "role": "Маршрутизатор запросов к agent-service, rag-service и другим микросервисам",
        "status": "running",
        "docs": "/docs"
    }