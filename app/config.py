# app/config.py
import os

SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-please").encode()
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1209600"))  # 14d

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "fitn")

DEFAULT_ORIGINS = ",".join(
    [
        "http://localhost",
        "http://localhost:81",
        "http://127.0.0.1",
        "http://127.0.0.1:81",
        "http://scrooge.mvconways.com:81",
    ]
)
FRONTEND_ORIGINS = os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_MAX_AGE = int(os.getenv("COOKIE_MAX_AGE", str(60 * 60 * 24 * 30)))  # 30d
