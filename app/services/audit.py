# app/services/audit.py
from datetime import datetime, timezone
from ..db import db

async def log_prompt_response(prompt: str, response: str):
    await db["prompts"].insert_one({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "response": response
    })
