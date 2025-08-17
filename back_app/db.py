import os
import motor.motor_asyncio
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "fitn")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def log_prompt_response(prompt: str, response: str):
    await db.prompts.insert_one({
        "timestamp": datetime.utcnow(),
        "prompt": prompt,
        "response": response
    })
