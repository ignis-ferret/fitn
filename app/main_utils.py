# app/main_utils.py
from typing import Dict
from .db import sel_col

async def build_plan_summary(uid_or_sid: str) -> Dict:
    # We only need the DB uid (ObjectId string). If you later enforce signed "sid" only,
    # make sure caller passes the decoded uid.
    uid = uid_or_sid  # kept for compatibility
    out = {
        "sleep": {"exists": False, "updated_at": None, "notes": "No sleep plan yet."},
        "diet": {"exists": False, "updated_at": None, "notes": "No diet plan yet."},
        "rewards": {
            "exists": False, "updated_at": None,
            "level1_count": 0, "level2_count": 0, "level3_count": 0,
        },
    }
    rs = await sel_col.find_one({"user_id": uid})
    if rs:
        out["rewards"]["exists"] = True
        out["rewards"]["updated_at"] = rs.get("updated_at")
        out["rewards"]["level1_count"] = len(rs.get("level1_codes", []))
        out["rewards"]["level2_count"] = len(rs.get("level2_codes", []))
        out["rewards"]["level3_count"] = len(rs.get("level3_choices", []))
    return out
