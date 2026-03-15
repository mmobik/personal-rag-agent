import httpx
from app.core.config import settings

OPENROUTER_URL = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"


def _headers() -> dict[str, str]:
    h = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_REFERER:
        h["HTTP-Referer"] = settings.OPENROUTER_REFERER
    if settings.OPENROUTER_TITLE:
        h["X-OpenRouter-Title"] = settings.OPENROUTER_TITLE
    return h


async def complete(messages: list[dict[str, str]], model: str | None = None) -> str:
    """Отправить сообщения в Open Router, вернуть текст ответа."""
    full_messages: list[dict[str, str]] = []
    if settings.OPENROUTER_SYSTEM_PROMPT:
        full_messages.append({"role": "system", "content": settings.OPENROUTER_SYSTEM_PROMPT})
    full_messages.extend(messages)
    payload = {
        "model": model or settings.OPENROUTER_MODEL,
        "messages": full_messages,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(OPENROUTER_URL, json=payload, headers=_headers())
        r.raise_for_status()
    data = r.json()
    choice = data.get("choices") or []
    if not choice:
        return ""
    return (choice[0].get("message") or {}).get("content") or ""
