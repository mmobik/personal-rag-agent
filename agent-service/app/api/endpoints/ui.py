from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(tags=["ui"])


@router.get("/ui/chat-history", response_class=HTMLResponse)
def chat_history_ui():
    template_path = Path(__file__).resolve().parents[2] / "templates" / "chat_history.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))

