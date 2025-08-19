# app/routers/pages.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

from ..template_loader import templates  # ✅ shared env
from ..deps import require_login_redirect
from ..security import parse_session_cookie   # ✅ decode sid -> uid
from ..main_utils import build_plan_summary

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("main.html", {"request": request, "user": None})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, _u=Depends(require_login_redirect)):
    sid = request.cookies.get("sid")
    uid = parse_session_cookie(sid) if sid else request.cookies.get("uid")
    summary = await build_plan_summary(uid)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": request.state.user, "summary": summary},
    )

@router.get("/intake", response_class=HTMLResponse)
async def intake_page(request: Request, _u=Depends(require_login_redirect)):
    return templates.TemplateResponse("intake.html", {"request": request})

@router.get("/rewards/", response_class=HTMLResponse)
async def rewards_page(request: Request, _u=Depends(require_login_redirect)):
    return templates.TemplateResponse("rewards.html", {"request": request})
