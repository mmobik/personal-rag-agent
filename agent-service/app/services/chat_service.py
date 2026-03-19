import json
from app.redis.client import client as redis_client
from app.services.llm_service import complete


HISTORY_MAX_MESSAGES = 20  # user+assistant вместе
HISTORY_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 дней


def _key(telegram_id: str) -> str:
    return f"chat:history:{telegram_id}"


def list_telegram_ids(limit: int = 500) -> list[str]:
    """
    Возвращает список telegram_id, для которых есть история.
    Используем SCAN (без KEYS), чтобы не блокировать Redis.
    """
    ids: list[str] = []
    cursor: int = 0
    pattern = "chat:history:*"
    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=200)
        for k in keys:
            # k вида chat:history:<telegram_id>
            if not isinstance(k, str):
                continue
            prefix = "chat:history:"
            if k.startswith(prefix):
                ids.append(k[len(prefix):])
                if len(ids) >= limit:
                    return sorted(set(ids))
        if cursor == 0:
            break
    return sorted(set(ids))


def delete_history(telegram_id: str) -> bool:
    return bool(redis_client.delete(_key(telegram_id)))


def delete_all_histories(limit: int = 5000) -> int:
    ids = list_telegram_ids(limit=limit)
    if not ids:
        return 0
    keys = [_key(tid) for tid in ids]
    return int(redis_client.delete(*keys))


def history_preview(telegram_id: str, last_n: int = 10) -> list[dict[str, str]]:
    raw_items = redis_client.lrange(_key(telegram_id), -last_n, -1)
    out: list[dict[str, str]] = []
    for raw in raw_items:
        msg = _deserialize_message(raw)
        if msg:
            out.append(msg)
    return out


def _serialize_message(msg: dict[str, str]) -> str:
    return json.dumps(msg, ensure_ascii=False)


def _deserialize_message(raw: str) -> dict[str, str] | None:
    try:
        data = json.loads(raw)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    role = data.get("role")
    content = data.get("content")
    if not isinstance(role, str) or not isinstance(content, str):
        return None
    return {"role": role, "content": content}


def load_history(telegram_id: str) -> list[dict[str, str]]:
    raw_items = redis_client.lrange(_key(telegram_id), 0, -1)
    out: list[dict[str, str]] = []
    for raw in raw_items:
        msg = _deserialize_message(raw)
        if msg:
            out.append(msg)
    return out


def append_message(telegram_id: str, role: str, content: str) -> None:
    k = _key(telegram_id)
    redis_client.rpush(k, _serialize_message({"role": role, "content": content}))
    # ограничиваем историю последними N сообщениями
    redis_client.ltrim(k, -HISTORY_MAX_MESSAGES, -1)
    redis_client.expire(k, HISTORY_TTL_SECONDS)


async def reply(telegram_id: str, message: str) -> str:
    """
    1) берём историю из Redis
    2) добавляем новое user сообщение
    3) вызываем LLM
    4) сохраняем assistant ответ в Redis
    """
    history = load_history(telegram_id)
    history.append({"role": "user", "content": message})
    answer = await complete(history)
    append_message(telegram_id, "user", message)
    append_message(telegram_id, "assistant", answer)
    return answer

