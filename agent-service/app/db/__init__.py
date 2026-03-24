"""
Database package
Содержит модели, подключение к БД и утилиты
"""

from .postgres import engine, Base, SessionLocal, get_db
from .models import User, ChatHistory, AgentSession, TelegramProfile, UIAdminProfile, UserType

__all__ = [
    'engine',
    'Base',
    'SessionLocal',
    'get_db',
    'User',
    'ChatHistory',
    'AgentSession',
    'TelegramProfile',
    'UIAdminProfile',
    'UserType',
]

version = "1.0.1"