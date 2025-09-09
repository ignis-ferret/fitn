# app/routers/auth_routes.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import COOKIE_MAX_AGE, COOKIE_SECURE
from ..db import users_col
from ..security import create_session_cookie, hash_password, verify_password
from ..template_loader import templates  # ✅ shared env

router = APIRouter(prefix="/auth")


@router.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request, err: str | None = None):
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "auth_signin.html", {"request": request, "err": err or ""}
    )


@router.post("/signin", response_class=HTMLResponse)
async def signin_submit(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    email_norm = email.lower().strip()
    user = await users_col.find_one({"email": email_norm})
    if not user or not verify_password(password, user.get("password_hash", "")):
        return templates.TemplateResponse(
            "auth_signin.html",
            {"request": request, "err": "Invalid email or password."},
            status_code=400,
        )
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(
        "uid",
        str(user["_id"]),
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    resp.set_cookie(
        "sid",
        create_session_cookie(str(user["_id"])),
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    return resp


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, err: str | None = None):
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        "auth_signup.html", {"request": request, "err": err or ""}
    )


@router.post("/signup", response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    email_norm = email.lower().strip()
    if not email_norm or not password:
        return templates.TemplateResponse(
            "auth_signup.html",
            {"request": request, "err": "Email and password are required."},
            status_code=400,
        )
    try:
        from datetime import datetime, timezone

        doc = {
            "name": name.strip(),
            "email": email_norm,
            "password_hash": hash_password(password),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = await users_col.insert_one(doc)
    except Exception:
        return templates.TemplateResponse(
            "auth_signup.html",
            {"request": request, "err": "Email already registered."},
            status_code=400,
        )

    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(
        "uid",
        str(res.inserted_id),
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    resp.set_cookie(
        "sid",
        create_session_cookie(str(res.inserted_id)),
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    return resp


@router.post("/signout")
async def signout():
    resp = RedirectResponse(url="/", status_code=303)
    for name in ("uid", "sid", "csrf"):
        resp.delete_cookie(name, path="/")
    return resp
