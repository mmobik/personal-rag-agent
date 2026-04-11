from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(tags=["ui"])

@router.get("/ui/admin", response_class=HTMLResponse)
def admin_panel_ui():
    """Админ панель - управление историей чатов"""
    template_path = Path(__file__).resolve().parents[2] / "templates" / "admin.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))

@router.get("/ui/chat-history", response_class=HTMLResponse)
def chat_history_ui():
    template_path = Path(__file__).resolve().parents[2] / "templates" / "chat_history.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))

@router.get("/ui/login", response_class=HTMLResponse)
def login_ui():
    template_path = Path(__file__).resolve().parents[2] / "templates" / "login.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))

@router.get("/ui/register", response_class=HTMLResponse)
def register_ui():
    template_path = Path(__file__).resolve().parents[2] / "templates" / "register.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))


@router.get("/ui/profile", response_class=HTMLResponse)
def profile_ui():
    """Страница профиля администратора"""
    template_path = Path(__file__).resolve().parents[2] / "templates" / "profile.html"
    return HTMLResponse(template_path.read_text(encoding="utf-8"))
