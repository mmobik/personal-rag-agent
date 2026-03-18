import httpx
from app.core.config import settings

OLLAMA_GENERATE_URL = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"


def _build_prompt(messages: list[dict[str, str]]) -> str:
    """
    Ollama /api/generate принимает prompt строкой.
    Минимальная стратегия: склеиваем историю в простой текст.
    """
    parts: list[str] = []
    for m in messages:
        role = (m.get("role") or "").strip() or "user"
        content = (m.get("content") or "").strip()
        if not content:
            continue
        parts.append(f"{role}: {content}")
    return "\n".join(parts) if parts else ""


async def complete(messages: list[dict[str, str]], model: str | None = None) -> str:
    """Отправить сообщения в Ollama, вернуть текст ответа."""
    prompt = _build_prompt(messages)
    payload = {
        "model": model or settings.OLLAMA_MODEL,
        "system": settings.OLLAMA_SYSTEM_PROMPT or "",
        "prompt": prompt,
        "stream": False,
    }
    # Первая генерация может занимать время (подгрузка модели).
    # Делаем таймаут выше, чтобы не получать ReadTimeout.
    async with httpx.AsyncClient(timeout=300.0) as client:
        r = await client.post(OLLAMA_GENERATE_URL, json=payload)
        if not r.is_success:
            return f"(LLM недоступна: HTTP {r.status_code})"
        data = r.json()
    return (data.get("response") or "").strip()
