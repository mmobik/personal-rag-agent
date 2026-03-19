from fastapi import APIRouter, HTTPException, Query

from app.services import chat_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/chat-histories")
def list_histories(limit: int = Query(500, ge=1, le=5000)):
    ids = chat_service.list_telegram_ids(limit=limit)
    return {"count": len(ids), "telegram_ids": ids}


@router.get("/chat-histories/{telegram_id}")
def get_history(telegram_id: str, last_n: int = Query(50, ge=1, le=500)):
    msgs = chat_service.history_preview(telegram_id, last_n=last_n)
    return {"telegram_id": telegram_id, "messages": msgs}


@router.delete("/chat-histories/{telegram_id}")
def delete_history(telegram_id: str):
    ok = chat_service.delete_history(telegram_id)
    if not ok:
        raise HTTPException(status_code=404, detail="history not found")
    return {"deleted": True, "telegram_id": telegram_id}


@router.delete("/chat-histories")
def delete_all(limit: int = Query(5000, ge=1, le=20000)):
    deleted = chat_service.delete_all_histories(limit=limit)
    return {"deleted": deleted}

