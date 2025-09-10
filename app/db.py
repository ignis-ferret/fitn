# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient

from .config import DB_NAME, MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
options_col = db["reward_options"]
sel_col = db["reward_selections"]
users_col = db["users"]
intake_col = db["intake_questions"]
