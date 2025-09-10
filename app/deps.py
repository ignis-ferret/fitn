# app/deps.py
from bson import ObjectId
from fastapi import HTTPException, Request, status

from .db import users_col
from .security import parse_session_cookie


async def get_user_by_id(uid: str):
    try:
        oid = ObjectId(uid)
    except Exception:
        return None
    return await users_col.find_one({"_id": oid})


def require_uid_cookie(request: Request) -> str:
    # Backward-compatible: try signed "sid", then fallback to plain "uid"
    sid = request.cookies.get("sid")
    uid = parse_session_cookie(sid) if sid else request.cookies.get("uid")
    if not uid:
        raise HTTPException(403, "Auth required")
    return uid


async def require_admin(request: Request) -> str:
    uid = require_uid_cookie(request)
    user = await get_user_by_id(uid)
    if not user:
        raise HTTPException(403, "Auth required")
    # tighten if/when you flip the flag on users
    # if not user.get("is_admin"):
    #     raise HTTPException(403, "Admin required")
    return uid


def require_login_redirect(request: Request):
    if not getattr(request.state, "user", None):
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/"},
        )
    return request.state.user
