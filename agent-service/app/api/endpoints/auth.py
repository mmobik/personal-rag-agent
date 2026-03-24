from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib
import secrets
import string
import re
from typing import Optional
from app.db import get_db, User, TelegramProfile, UIAdminProfile, UserType

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBasic()

# Pydantic модели
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str  # Изменено с username на full_name для UI

class TelegramUserCreate(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    chat_id: Optional[str] = None

# Вспомогательные функции
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password:
        return False
    salt = stored_password[:32]
    stored_pwdhash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_pwdhash

def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    if not any(c.isupper() for c in password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"
    if not any(c.islower() for c in password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"
    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать хотя бы одну цифру"
    if not re.search(r"[!@#$%^&*]", password):
        return False, "Пароль должен содержать хотя бы один специальный символ (!@#$%^&*)"
    return True, ""

# Эндпоинты для UI админов
@router.post("/register")
def register_ui_admin(body: RegisterRequest, db: Session = Depends(get_db)):
    """Регистрация UI администратора"""
    try:
        # Проверка пароля
        is_valid, message = validate_password(body.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Проверка существующего пользователя
        existing_user = db.query(User).filter(
            User.email == body.email,
            User.user_type == UserType.UI_ADMIN
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        
        # Создаем базового пользователя
        user = User(
            user_type=UserType.UI_ADMIN,
            email=body.email,
            password_hash=hash_password(body.password),
            is_active=True,
            is_admin=True  # UI админы всегда админы
        )
        db.add(user)
        db.flush()
        
        # Создаем UI профиль
        ui_profile = UIAdminProfile(
            user_id=user.id,
            full_name=body.full_name,
            role="admin"
        )
        db.add(ui_profile)
        
        # Генерируем API ключ
        user.generate_api_key()
        
        db.commit()
        db.refresh(user)
        
        return {
            "message": "Администратор успешно зарегистрирован",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": body.full_name,
                "api_key": user.api_key
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации: {str(e)}")

@router.post("/login")
def login_ui_admin(body: LoginRequest, db: Session = Depends(get_db)):
    """Вход UI администратора"""
    user = db.query(User).filter(
        User.email == body.email,
        User.user_type == UserType.UI_ADMIN
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт не активен",
        )
    
    if not verify_password(user.password_hash, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    # Обновляем время последнего входа
    if user.ui_admin_profile:
        from datetime import datetime
        user.ui_admin_profile.last_login = datetime.utcnow()
        db.commit()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.ui_admin_profile.full_name if user.ui_admin_profile else None,
        "api_key": user.api_key,
        "is_admin": user.is_admin
    }

# Эндпоинт для Telegram бота (создание пользователя)
@router.post("/telegram/user")
def create_telegram_user(body: TelegramUserCreate, db: Session = Depends(get_db)):
    """Создание пользователя через Telegram (вызывается из бота)"""
    try:
        # Проверяем существующий профиль
        existing_profile = db.query(TelegramProfile).filter(
            TelegramProfile.telegram_id == body.telegram_id
        ).first()
        
        if existing_profile:
            return {
                "id": existing_profile.user.id,
                "telegram_id": body.telegram_id,
                "status": "already_exists"
            }
        
        # Создаем базового пользователя
        user = User(
            user_type=UserType.TELEGRAM,
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.flush()
        
        # Создаем Telegram профиль
        telegram_profile = TelegramProfile(
            user_id=user.id,
            telegram_id=body.telegram_id,
            username=body.username,
            first_name=body.first_name,
            last_name=body.last_name,
            chat_id=body.chat_id or body.telegram_id
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
        raise HTTPException(status_code=500, detail=f"Ошибка создания пользователя: {str(e)}")

# Общий эндпоинт для получения текущего пользователя
@router.get("/me")
def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    """Получение текущего пользователя (по API key или email/password)"""
    
    # Пробуем найти по API key
    user = db.query(User).filter(User.api_key == credentials.password).first()
    
    # Если не нашли, пробуем по email/password
    if not user:
        user = db.query(User).filter(
            User.email == credentials.username,
            User.user_type == UserType.UI_ADMIN
        ).first()
        
        if not user or not verify_password(user.password_hash, credentials.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Basic"},
            )
    
    # Формируем ответ в зависимости от типа пользователя
    response = {
        "id": user.id,
        "user_type": user.user_type.value,
        "is_admin": user.is_admin
    }
    
    if user.user_type == UserType.UI_ADMIN and user.ui_admin_profile:
        response.update({
            "email": user.email,
            "full_name": user.ui_admin_profile.full_name,
            "role": user.ui_admin_profile.role
        })
    elif user.user_type == UserType.TELEGRAM and user.telegram_profile:
        response.update({
            "telegram_id": user.telegram_profile.telegram_id,
            "username": user.telegram_profile.username,
            "first_name": user.telegram_profile.first_name,
            "last_name": user.telegram_profile.last_name
        })
    
    return response

# Генерация пароля (общая)
@router.get("/generate-password")
def generate_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return {"password": password}