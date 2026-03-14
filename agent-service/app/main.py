from fastapi import FastAPI

app = FastAPI(title="Agent Service")

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
