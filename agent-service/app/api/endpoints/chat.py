from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import reply

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    telegram_id: str
    message: str


@router.post("")
async def chat(body: ChatRequest):
    """Принять сообщение, вернуть ответ LLM."""
    response_text = await reply(body.telegram_id, body.message)
    return {"response": response_text}
