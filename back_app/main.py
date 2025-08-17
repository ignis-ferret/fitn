# main.py

from datetime import datetime, timezone
import os
import binascii
import hashlib

from bson import ObjectId
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.templating import Jinja2Templates

from services.openai_service import ask_chatgpt
from db import log_prompt_response
from models import RewardTree, SelectionPayload, IntakeQuestion

# ----------------------------
# App & Config
# ----------------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "fitn")
FRONTEND_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost,http://localhost:81,http://dev.mvconways.com:81"
).split(",")

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_MAX_AGE = int(os.getenv("COOKIE_MAX_AGE", str(60 * 60 * 24 * 30)))  # 30d

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
options_col = db["reward_options"]
sel_col = db["reward_selections"]
users_col = db["users"]
intake_col = db["intake_questions"]

# ----------------------------
# Utilities
# ----------------------------

@app.get("/healthz")
async def healthz():
    return {"ok": True}

def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(dk).decode()}"

def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = binascii.unhexlify(salt_hex.encode())
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return binascii.hexlify(dk).decode() == hash_hex
    except Exception:
        return False

async def _get_user_by_cookie_uid(uid: str):
    try:
        oid = ObjectId(uid)
    except Exception:
        return None
    return await users_col.find_one({"_id": oid})

def _require_uid_cookie(request: Request) -> str:
    uid = request.cookies.get("uid")
    if not uid:
        raise HTTPException(403, "Auth required")
    return uid

async def _require_admin(request: Request) -> str:
    uid = _require_uid_cookie(request)
    user = await _get_user_by_cookie_uid(uid)
    if not user:
        raise HTTPException(403, "Auth required")
    # Optional: enforce admin roles
    # if not user.get("is_admin"): raise HTTPException(403, "Admin required")
    return uid

# attach user to request.state on every request
@app.middleware("http")
async def inject_user(request: Request, call_next):
    uid = request.cookies.get("uid")
    request.state.user = await _get_user_by_cookie_uid(uid) if uid else None
    return await call_next(request)

# dependency: redirect to "/" if not signed in
def require_login_redirect(request: Request):
    if not getattr(request.state, "user", None):
        # 307 preserves method if needed; here it's a GET so it's fine
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/"},
        )
    return request.state.user

# ----------------------------
# Startup tasks
# ----------------------------
@app.on_event("startup")
async def _ensure_user_index():
    await users_col.create_index("email", unique=True)

@app.on_event("startup")
async def _ensure_intake_index():
    await intake_col.create_index("id", unique=True)

# ----------------------------
# Pages
# ----------------------------
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    # Signed-in users go straight to dashboard
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("main.html", {"request": request, "user": None})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, _u=Depends(require_login_redirect)):
    uid = request.cookies.get("uid")
    summary = await build_plan_summary(uid)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": request.state.user, "summary": summary},
    )

@app.get("/intake", response_class=HTMLResponse)
async def intake_page(request: Request, _u=Depends(require_login_redirect)):
    # placeholder page until the interview wizard is built
    return templates.TemplateResponse("intake.html", {"request": request})

@app.get("/deva/", response_class=HTMLResponse)
async def dev_page(request: Request, _u=Depends(require_login_redirect)):
    return templates.TemplateResponse("deva.html", {"request": request})

@app.post("/deva/", response_class=HTMLResponse)
async def handle_prompt(request: Request, prompt: str = Form(...), _u=Depends(require_login_redirect)):
    response = await ask_chatgpt(prompt)
    await log_prompt_response(prompt, response)
    return templates.TemplateResponse("deva.html", {"request": request, "prompt": prompt, "response": response})

@app.get("/rewards/", response_class=HTMLResponse)
async def rewards_page(request: Request, _u=Depends(require_login_redirect)):
    return templates.TemplateResponse("rewards.html", {"request": request})

# ----------------------------
# Rewards API
# ----------------------------
@app.get("/api/options")
async def get_options():
    doc = await options_col.find_one({})
    if not doc:
        return {"groups": []}
    doc.pop("_id", None)
    return doc

@app.post("/api/selections")
async def post_selection(request: Request, payload: SelectionPayload):
    # Auth: bind selection to the signed-in user
    uid = _require_uid_cookie(request)
    user = await _get_user_by_cookie_uid(uid)
    if not user:
        raise HTTPException(403, "Auth required")

    # Validate against current options tree
    tree_doc = await options_col.find_one({})
    if not tree_doc:
        raise HTTPException(400, "Options not loaded")
    tree = RewardTree(**{k: v for k, v in tree_doc.items() if k != "_id"})

    # Validate Level1 and Level2 codes
    lvl1_set = {g.code for g in tree.groups}
    for code in payload.level1_codes:
        if code not in lvl1_set:
            raise HTTPException(400, f"Invalid level1 code: {code}")

    lvl2_set = {cat.code for g in tree.groups for cat in g.categories}
    for code in payload.level2_codes:
        if code not in lvl2_set:
            raise HTTPException(400, f"Invalid level2 code: {code}")

    # Validate Level3: exactly one variant per selected item_code
    items_map: dict[str, set[str]] = {}
    for g in tree.groups:
        for cat in g.categories:
            for it in cat.items:
                items_map[it.code] = {v.code for v in it.variations}

    seen_items = set()
    for ch in payload.level3_choices:
        item_code = ch.get("item_code")
        var_code = ch.get("variant_code")
        if not item_code or not var_code:
            raise HTTPException(400, "Missing item_code/variant_code")
        if item_code not in items_map:
            raise HTTPException(400, f"Invalid item_code: {item_code}")
        if var_code not in items_map[item_code]:
            raise HTTPException(400, f"Variant not in item: {var_code}")
        if item_code in seen_items:
            raise HTTPException(400, f"Multiple variants for item {item_code}")
        seen_items.add(item_code)

    # Persist (bind to uid) + timestamp
    record = payload.dict()
    record["user_id"] = uid
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    await sel_col.update_one({"user_id": uid}, {"$set": record}, upsert=True)
    return {"ok": True}

# helper: build dashboard plan summary
async def build_plan_summary(uid: str) -> dict:
    out = {
        "sleep": {"exists": False, "updated_at": None, "notes": "No sleep plan yet."},
        "diet": {"exists": False, "updated_at": None, "notes": "No diet plan yet."},
        "rewards": {
            "exists": False, "updated_at": None,
            "level1_count": 0, "level2_count": 0, "level3_count": 0,
        },
    }

    # If later you add sleep_plans / diet_plans collections, read them here.
    # Example:
    # sp = await db["sleep_plans"].find_one({"user_id": uid}, {"_id": 0, "updated_at": 1})
    # if sp: out["sleep"] = {"exists": True, "updated_at": sp.get("updated_at"), "notes": ""}

    rs = await sel_col.find_one({"user_id": uid})
    if rs:
        out["rewards"]["exists"] = True
        out["rewards"]["updated_at"] = rs.get("updated_at")
        out["rewards"]["level1_count"] = len(rs.get("level1_codes", []))
        out["rewards"]["level2_count"] = len(rs.get("level2_codes", []))
        out["rewards"]["level3_count"] = len(rs.get("level3_choices", []))

    return out

# ----------------------------
# Auth (Sign In / Sign Up)
# ----------------------------
@app.get("/auth/signin", response_class=HTMLResponse)
async def signin_page(request: Request, err: str | None = None):
    # Already signed in? Go to dashboard.
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth_signin.html", {"request": request, "err": err or ""})

@app.post("/auth/signin", response_class=HTMLResponse)
async def signin_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    email_norm = email.lower().strip()
    user = await users_col.find_one({"email": email_norm})
    if not user or not _verify_password(password, user.get("password_hash", "")):
        return templates.TemplateResponse("auth_signin.html", {"request": request, "err": "Invalid email or password."}, status_code=400)
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
    return resp

@app.get("/auth/signup", response_class=HTMLResponse)
async def signup_page(request: Request, err: str | None = None):
    # Already signed in? Go to dashboard.
    if request.state.user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth_signup.html", {"request": request, "err": err or ""})

@app.post("/auth/signup", response_class=HTMLResponse)
async def signup_submit(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    email_norm = email.lower().strip()
    if not email_norm or not password:
        return templates.TemplateResponse("auth_signup.html", {"request": request, "err": "Email and password are required."}, status_code=400)
    try:
        doc = {
            "name": name.strip(),
            "email": email_norm,
            "password_hash": _hash_password(password),
            "created_at": datetime.now(timezone.utc).isoformat(),
            # "is_admin": True,  # uncomment to bootstrap your own admin user
        }
        res = await users_col.insert_one(doc)
    except Exception:
        return templates.TemplateResponse("auth_signup.html", {"request": request, "err": "Email already registered."}, status_code=400)

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
    return resp

# ----------------------------
# Admin: Intake CRUD
# ----------------------------
@app.get("/admin/intake", response_class=HTMLResponse)
async def admin_intake_page(request: Request, _uid: str = Depends(_require_admin)):
    return templates.TemplateResponse("admin_intake.html", {"request": request})

@app.get("/api/admin/intake")
async def list_intake(grouped: int = 1, _uid: str = Depends(_require_admin)):
    cur = intake_col.find({}, {"_id": 0}).sort("id", 1)
    items = [x async for x in cur]
    if not grouped:
        return {"items": items}
    out: dict[str, list[dict]] = {}
    for q in items:
        out.setdefault(q["section"], []).append(q)
    return {"sections": out}

@app.post("/api/admin/intake")
async def create_intake(q: dict, _uid: str = Depends(_require_admin)):
    # Server-side cleanup for optional
    if "optional" in q and q["optional"] is None:
        del q["optional"]
    try:
        IntakeQuestion(**q)  # validate
        await intake_col.insert_one(q)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.put("/api/admin/intake/{qid}")
async def update_intake(qid: str, q: dict, _uid: str = Depends(_require_admin)):
    if "optional" in q and q["optional"] is None:
        del q["optional"]
    try:
        if q.get("id") and q["id"] != qid:
            raise HTTPException(400, "id mismatch")
        IntakeQuestion(**{**q, "id": qid})
        res = await intake_col.update_one({"id": qid}, {"$set": q})
        if res.matched_count == 0:
            raise HTTPException(404, "not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.delete("/api/admin/intake/{qid}")
async def delete_intake(qid: str, _uid: str = Depends(_require_admin)):
    res = await intake_col.delete_one({"id": qid})
    if res.deleted_count == 0:
        raise HTTPException(404, "not found")
    return {"ok": True}
