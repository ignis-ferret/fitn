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

    If the user document does not yet exist, raise an error. If body fat
    percentage was not provided, estimate it using the Deurenberg formula.
    """

    def estimate_body_fat(ans: Dict[str, Any]) -> float | None:
        try:
            weight = float(ans.get("current_weight_lbs"))
            height = float(ans.get("height_inches"))
            age = float(ans.get("age"))
            gender = (ans.get("gender") or "").lower()
            bmi = (weight / (height * height)) * 703
            sex = 1 if gender == "male" else 0
            return round(1.20 * bmi + 0.23 * age - 10.8 * sex - 5.4, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    answers = dict(payload.answers)
    if not answers.get("body_fat_percentage"):
        est = estimate_body_fat(answers)
        if est is not None:
            answers["body_fat_percentage"] = est

    oid = ObjectId(uid)
    res = await users_col.update_one(
        {"_id": oid}, {"$set": {"intake_answers": answers}}, upsert=False
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="user not found")
    return {"ok": True}
