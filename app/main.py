# app/main.py
from pathlib import Path  # ✅ add this

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_ORIGINS
from .db import intake_col, users_col
from .deps import get_user_by_id
from .routers import health as health_router
from .routers.admin_intake import router as admin_router
from .routers.auth_routes import router as auth_router
from .routers.deva import router as deva_router
from .routers.intake import router as intake_router
from .routers.pages import router as pages_router
from .routers.rewards import router as rewards_router
from .security import parse_session_cookie

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI()

app.include_router(health_router.router)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health
@app.get("/healthz")
async def healthz():
    return {"ok": True}


# Attach user to request.state on every request
@app.middleware("http")
async def inject_user(request: Request, call_next):
    uid = None
    sid = request.cookies.get("sid")
    if sid:
        uid = parse_session_cookie(sid)
    if not uid:
        uid = request.cookies.get("uid")

    request.state.user = await get_user_by_id(uid) if uid else None
    return await call_next(request)


# Startup tasks
@app.on_event("startup")
async def _ensure_user_index():
    await users_col.create_index("email", unique=True)


@app.on_event("startup")
async def _ensure_intake_index():
    await intake_col.create_index("id", unique=True)


# Routers
app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(rewards_router)
app.include_router(admin_router)
app.include_router(deva_router)
app.include_router(intake_router)
