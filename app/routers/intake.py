# app/routers/intake.py
"""Endpoints for the intake wizard used to create a new plan."""
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..db import intake_col, users_col
from ..deps import require_uid_cookie

router = APIRouter()

@router.get("/api/intake/questions")
async def get_intake_questions(
    _uid: str = Depends(require_uid_cookie),
) -> Dict[str, Any]:
    """Return all intake questions ordered by their id.

    The client side wizard uses these questions to render the interview.
    """
    cur = intake_col.find({}, {"_id": 0}).sort("id", 1)
    questions = [q async for q in cur]
    return {"questions": questions}

class IntakeAnswers(BaseModel):
    """Payload for saving intake answers."""

    answers: Dict[str, Any]

@router.post("/api/intake/answers")
async def save_intake_answers(
    payload: IntakeAnswers, uid: str = Depends(require_uid_cookie)
) -> Dict[str, Any]:
    """Store the provided answers on the user document.

    If the user document does not yet exist, raise an error.
    """
    oid = ObjectId(uid)
    res = await users_col.update_one(
        {"_id": oid}, {"$set": {"intake_answers": payload.answers}}, upsert=False
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    return {"ok": True}
