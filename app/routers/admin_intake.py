# app/routers/admin_intake.py
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

# app/routers/admin_intake.py (add these imports near the top)
from pydantic import BaseModel
from pymongo import UpdateOne

from ..db import intake_col
from ..deps import require_admin
from ..template_loader import templates  # ✅ shared env

router = APIRouter()


@router.get("/admin/intake", response_class=HTMLResponse)
async def admin_intake_page(request: Request, _uid: str = Depends(require_admin)):
    return templates.TemplateResponse("admin_intake.html", {"request": request})


@router.get("/api/admin/intake")
async def list_intake(grouped: int = 1, _uid: str = Depends(require_admin)):
    cur = intake_col.find({}, {"_id": 0}).sort("id", 1)
    items = [x async for x in cur]
    if not grouped:
        return {"items": items}
    out: dict[str, list[dict]] = {}
    for q in items:
        out.setdefault(q["section"], []).append(q)
    return {"sections": out}


# app/routers/admin_intake.py (append at the bottom of the file)
class IntakeQuestion(BaseModel):
    id: str
    section: str
    text: str
    type: str
    variable_name: str
    options: Optional[List[Dict[str, Any]]] = None
    range: Optional[Dict[str, Any]] = None
    optional: Optional[bool] = None
    conditional_on: Optional[Dict[str, Any]] = None
    max_selections: Optional[int] = None
    sort_index: Optional[int] = None


@router.post("/api/admin/intake")
async def create_question(
    q: IntakeQuestion, _uid: str = Depends(require_admin)
) -> Dict[str, Any]:
    if await intake_col.find_one({"id": q.id}):
        raise HTTPException(status_code=400, detail="id exists")
    await intake_col.insert_one(q.dict(exclude_none=True))
    return {"ok": True}


@router.put("/api/admin/intake/{qid}")
async def update_question(
    qid: str, q: IntakeQuestion, _uid: str = Depends(require_admin)
) -> Dict[str, Any]:
    if q.id != qid and await intake_col.find_one({"id": q.id}):
        raise HTTPException(status_code=400, detail="id exists")
    res = await intake_col.update_one({"id": qid}, {"$set": q.dict(exclude_none=True)})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


@router.delete("/api/admin/intake/{qid}")
async def delete_question(
    qid: str, _uid: str = Depends(require_admin)
) -> Dict[str, Any]:
    res = await intake_col.delete_one({"id": qid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


class ReorderItem(BaseModel):
    id: str
    sort_index: int


class ReorderPayload(BaseModel):
    section: str
    order: List[ReorderItem]


@router.post("/api/admin/intake/reorder")
async def reorder_intake(payload: ReorderPayload, _uid: str = Depends(require_admin)):
    if not payload.order:
        raise HTTPException(status_code=400, detail="empty order")

    # Build bulk ops: ensure we only update items within the provided section
    ops = [
        UpdateOne(
            {"id": it.id, "section": payload.section},
            {"$set": {"sort_index": it.sort_index}},
            upsert=False,
        )
        for it in payload.order
    ]

    if not ops:
        return {"ok": True, "updated": 0}

    res = await intake_col.bulk_write(ops, ordered=False)
    return {"ok": True, "updated": res.modified_count}
