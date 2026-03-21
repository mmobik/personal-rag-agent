from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib
import secrets
import re
from app.db import get_db, User

router = APIRouter(prefix="/auth", tags=["authentication"])

security = HTTPBasic()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

class ConfirmEmailRequest(BaseModel):
    token: str

def hash_password(password: str) -> str:
    """Хэширует пароль с солью"""
    salt = secrets.token_hex(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwdhash.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Проверяет пароль"""
    salt = stored_password[:32]
    stored_pwdhash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwdhash.hex() == stored_pwdhash

def validate_password(password: str) -> tuple[bool, str]:
    """Проверяет требования к паролю"""
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

def generate_confirmation_token() -> str:
    """Генерирует токен подтверждения email"""
    return secrets.token_urlsafe(32)

@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Проверка требований к паролю
        is_valid, message = validate_password(body.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Проверка существования пользователя
        existing_user = db.query(User).filter(User.email == body.email).first()
        if existing_user:
            if existing_user.is_active:
                raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
            else:
                # Если пользователь существует но не активен, обновляем данные
                existing_user.username = body.username
                existing_user.password_hash = hash_password(body.password)
                user = existing_user
        else:
            # Создание нового пользователя
            user = User(
                email=body.email,
                username=body.username,
                password_hash=hash_password(body.password),
                is_active=False
            )
            db.add(user)
        
        # Генерируем API ключ если его нет
        if not user.api_key:
            user.generate_api_key()
        
        db.commit()
        
        return {
            "message": "Пользователь успешно зарегистрирован. Проверьте ваш email для подтверждения.",
            "confirmation_required": True
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации: {str(e)}")

@router.get("/generate-password")
def generate_password():
    """Генерирует случайный пароль"""
    import string
    import secrets
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return {"password": password}

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт не подтвержден. Проверьте ваш email.",
        )
    
    if not user.password_hash or not verify_password(user.password_hash, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "api_key": user.api_key,
        "is_admin": user.is_admin
    }

@router.get("/me")
def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.username).first()
    if not user or not user.password_hash or not verify_password(user.password_hash, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_admin": user.is_admin
    }
