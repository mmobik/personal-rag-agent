from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import complete

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    telegram_id: str
    message: str


@router.post("")
async def chat(body: ChatRequest):
    """Принять сообщение, вернуть ответ LLM."""
    messages = [{"role": "user", "content": body.message}]
    response_text = await complete(messages)
    return {"response": response_text}
