from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.services.chat_service import reply
from app.db import get_db, User, TelegramProfile

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    telegram_id: Optional[str] = None
    user_id: Optional[int] = None
    message: str

@router.post("")
async def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """Принять сообщение, вернуть ответ LLM."""
    
    # Определяем пользователя
    user = None
    if body.user_id:
        user = db.query(User).filter(User.id == body.user_id).first()
    elif body.telegram_id:
        telegram_profile = db.query(TelegramProfile).filter(
            TelegramProfile.telegram_id == body.telegram_id
        ).first()
        if telegram_profile:
            user = telegram_profile.user
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Передаем user_id в сервис
    response_text = await reply(user.id, body.message)
    return {"response": response_text}