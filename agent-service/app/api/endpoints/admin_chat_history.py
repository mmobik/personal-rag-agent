from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services import chat_service
from app.db import get_db, TelegramProfile

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/chat-histories")
def list_histories(limit: int = Query(500, ge=1, le=5000), db: Session = Depends(get_db)):
    user_ids = chat_service.list_telegram_ids(limit=limit)
    
    # Конвертируем user_ids в telegram_ids
    telegram_ids = []
    for user_id in user_ids:
        profile = db.query(TelegramProfile).filter(
            TelegramProfile.user_id == int(user_id)
        ).first()
        if profile:
            telegram_ids.append(profile.telegram_id)
        else:
            telegram_ids.append(user_id)
    
    return {"count": len(telegram_ids), "telegram_ids": telegram_ids}

@router.get("/chat-histories/{telegram_id}")
def get_history(telegram_id: str, last_n: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    # Находим user_id по telegram_id
    profile = db.query(TelegramProfile).filter(
        TelegramProfile.telegram_id == telegram_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(profile.user_id)
    msgs = chat_service.history_preview(user_id, last_n=last_n)
    return {"telegram_id": telegram_id, "messages": msgs}

@router.delete("/chat-histories/{telegram_id}")
def delete_history(telegram_id: str, db: Session = Depends(get_db)):
    profile = db.query(TelegramProfile).filter(
        TelegramProfile.telegram_id == telegram_id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(profile.user_id)
    ok = chat_service.delete_history(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="history not found")
    return {"deleted": True, "telegram_id": telegram_id}

@router.delete("/chat-histories")
def delete_all(limit: int = Query(5000, ge=1, le=20000)):
    deleted = chat_service.delete_all_histories(limit=limit)
    return {"deleted": deleted}