from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db import get_db, User, TelegramProfile, UserType

router = APIRouter(prefix="/users", tags=["users"])

class TelegramUserCreate(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@router.post("", status_code=201)
def create_telegram_user(body: TelegramUserCreate, db: Session = Depends(get_db)):
    """Создание пользователя Telegram (для бота)"""
    try:
        # Проверяем существование
        existing_profile = db.query(TelegramProfile).filter(
            TelegramProfile.telegram_id == body.telegram_id
        ).first()
        
        if existing_profile:
            return {
                "id": existing_profile.user.id,
                "telegram_id": body.telegram_id,
                "status": "already_exists"
            }
        
        # Создаем пользователя
        user = User(
            user_type=UserType.TELEGRAM,
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.flush()
        
        # Создаем профиль
        telegram_profile = TelegramProfile(
            user_id=user.id,
            telegram_id=body.telegram_id,
            username=body.username,
            first_name=body.first_name,
            last_name=body.last_name
        )
        db.add(telegram_profile)
        
        # Генерируем API ключ
        user.generate_api_key()
        
        db.commit()
        db.refresh(user)
        
        return {
            "id": user.id,
            "telegram_id": body.telegram_id,
            "api_key": user.api_key,
            "status": "created"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")