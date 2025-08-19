# app/security.py
from datetime import datetime, timezone
import os, binascii, hashlib, base64, hmac

from .config import SESSION_SECRET, SESSION_TTL_SECONDS

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{binascii.hexlify(salt).decode()}:{binascii.hexlify(dk).decode()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = binascii.unhexlify(salt_hex.encode())
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), hash_hex)
    except Exception:
        return False

def _sign(value: bytes) -> str:
    mac = hmac.new(SESSION_SECRET, value, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")

def _b64(s: bytes) -> str:
    return base64.urlsafe_b64encode(s).decode().rstrip("=")

def _ub64(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def create_session_cookie(user_id: str) -> str:
    ts = str(int(datetime.now(timezone.utc).timestamp()))
    payload = f"{user_id}|{ts}".encode()
    sig = _sign(payload)
    return f"{_b64(payload)}.{sig}"

def parse_session_cookie(cookie_val: str) -> str | None:
    try:
        payload_b64, sig = cookie_val.split(".", 1)
        payload = _ub64(payload_b64)
        if _sign(payload) != sig:
            return None
        user_id, ts = payload.decode().split("|", 1)
        if (int(datetime.now(timezone.utc).timestamp()) - int(ts)) > SESSION_TTL_SECONDS:
            return None
        return user_id
    except Exception:
        return None
