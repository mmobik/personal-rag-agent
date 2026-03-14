import httpx
from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
async def create_user(request: Request):
    """Прокси: передаёт запрос в agent-service (сохранение в PostgreSQL)."""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{settings.AGENT_SERVICE_URL}/api/v1/users",
            json=body,
            timeout=10.0,
        )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()
