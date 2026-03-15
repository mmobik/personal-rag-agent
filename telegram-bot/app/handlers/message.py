import httpx
from aiogram import types
from app.core.config import settings

async def cmd_message(message: types.Message):
    text = message.text
    if not text or not text.strip():
        await message.answer("(не текст)")
        return
    user = message.from_user
    payload = {
        "telegram_id": str(user.id),
        "message": text.strip(),
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(
                f"{settings.API_GATEWAY_URL}/api/v1/chat",
                json=payload,
            )
        if r.status_code == 200:
            data = r.json()
            reply = (data.get("response") or "").strip() or "(нет ответа)"
            await message.answer(reply)
        else:
            await message.answer("Сервис временно недоступен.")
    except Exception:
        await message.answer("Сервис временно недоступен.")

def register_handlers(dp):
    dp.message.register(cmd_message)
