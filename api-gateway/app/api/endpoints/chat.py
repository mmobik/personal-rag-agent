import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    telegram_id: Optional[str] = None
    user_id: Optional[int] = None
    message: str


@router.post("", 
    summary="Отправить сообщение в чат",
    description="Проксирует запрос в agent-service для получения ответа от LLM")
async def chat(chat_data: ChatRequest):
    """
    Отправляет сообщение пользователя в LLM и возвращает ответ.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.AGENT_SERVICE_URL}/api/v1/chat",
            json=chat_data.dict(),
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()