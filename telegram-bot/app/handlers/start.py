import httpx
from aiogram import types
from aiogram.filters import Command
from app.core.config import settings

async def cmd_start(message: types.Message):
    user = message.from_user
    payload = {
        "telegram_id": str(user.id),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.API_GATEWAY_URL}/api/v1/users",
                json=payload,
                timeout=5.0,
            )
        if response.status_code in (200, 201):
            pass  # пользователь сохранён в PostgreSQL через agent-service
    except Exception:
        pass  # не падаем, если сервис недоступен
    await message.answer("Привет, я цифровой ассистент")

def register_handlers(dp):
    dp.message.register(cmd_start, Command(commands=["start","help"]))
