import httpx
from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(request: Request):
    """Прокси: передаёт запрос в agent-service (LLM)."""
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.AGENT_SERVICE_URL}/api/v1/chat",
            json=body,
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
