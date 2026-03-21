from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.postgres import Base
import secrets
import string
import re

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)  # Обязательное поле
    password_hash = Column(String, nullable=False)  # Обязательное поле
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=False)  # По умолчанию неактивен до подтверждения email
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def generate_api_key(self):
        """Генерирует уникальный API ключ из 16 символов"""
        characters = string.ascii_letters + string.digits
        self.api_key = ''.join(secrets.choice(characters) for _ in range(16))
    
    def generate_password(self, length=12):
        """Генерирует случайный пароль"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))



class ChatHistory(Base):
    """История чатов"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    telegram_id = Column(String, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentSession(Base):
    """Сессии агентов"""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String, unique=True, index=True)
    context = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
