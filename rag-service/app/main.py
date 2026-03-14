from fastapi import FastAPI
from app.api.endpoints import health

app = FastAPI(title="RAG Service")

app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def read_root():
    return {
        "name": "RAG Service",
        "role": "Векторный поиск с использованием Qdrant",
        "status": "running",
        "docs": "/docs"
    }
