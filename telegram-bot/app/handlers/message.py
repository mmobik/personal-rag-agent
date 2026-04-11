import httpx
from aiogram import types
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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
    
    # ДЕТАЛЬНАЯ ОТЛАДКА
    url = f"{settings.API_GATEWAY_URL}/api/v1/chat"
    logger.info(f"🔍 Sending request to: {url}")
    logger.info(f"📦 Payload: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload)
            logger.info(f"✅ Response status: {r.status_code}")
            logger.info(f"📄 Response body: {r.text[:500]}")
            
        if r.status_code == 200:
            data = r.json()
            reply = (data.get("response") or "").strip() or "(нет ответа)"
            await message.answer(reply)
        else:
            await message.answer(f"Сервис временно недоступен. Код: {r.status_code}")
    except Exception as e:
        logger.error(f"❌ Exception: {e}", exc_info=True)
        await message.answer("Сервис временно недоступен.")

def register_handlers(dp):
    dp.message.register(cmd_message)