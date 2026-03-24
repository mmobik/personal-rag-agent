from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base
import secrets
import string
import enum

class UserType(enum.Enum):
    TELEGRAM = "telegram"
    UI_ADMIN = "ui_admin"

class User(Base):
    """Базовая модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(Enum(UserType), nullable=False, default=UserType.TELEGRAM)
    email = Column(String, unique=True, index=True, nullable=True)  # Только для UI_ADMIN
    password_hash = Column(String, nullable=True)  # Только для UI_ADMIN
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    telegram_profile = relationship("TelegramProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    ui_admin_profile = relationship("UIAdminProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def generate_api_key(self):
        """Генерирует API ключ"""
        characters = string.ascii_letters + string.digits
        self.api_key = ''.join(secrets.choice(characters) for _ in range(32))

class TelegramProfile(Base):
    """Профиль Telegram пользователя"""
    __tablename__ = "telegram_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    chat_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="telegram_profile")

class UIAdminProfile(Base):
    """Профиль UI администратора"""
    __tablename__ = "ui_admin_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="admin")
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="ui_admin_profile")

class ChatHistory(Base):
    """История чатов"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    source = Column(String, default="telegram")  # telegram, ui_web, api
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")

class AgentSession(Base):
    """Сессии агентов"""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    session_id = Column(String, unique=True, index=True)
    context = Column(Text, nullable=True)
    source = Column(String, default="telegram")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")