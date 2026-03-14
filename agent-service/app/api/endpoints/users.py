from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db, User

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    telegram_id: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


@router.post("", status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """Сохранить пользователя в PostgreSQL (вызов из бота при /start)."""
    existing = db.query(User).filter(User.telegram_id == body.telegram_id).first()
    if existing:
        return {"id": existing.id, "telegram_id": existing.telegram_id, "status": "already_exists"}
    user = User(
        telegram_id=body.telegram_id,
        username=body.username,
        first_name=body.first_name,
        last_name=body.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "telegram_id": user.telegram_id, "status": "created"}
