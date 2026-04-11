import httpx
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["users"])

class TelegramUserCreate(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("", status_code=201)
async def create_user(user_data: TelegramUserCreate):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.AGENT_SERVICE_URL}/api/v1/users",
            json=user_data.dict(),
            timeout=10.0,
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()

