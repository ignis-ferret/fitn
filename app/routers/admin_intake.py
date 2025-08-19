# app/routers/admin_intake.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..template_loader import templates  # ✅ shared env
from ..deps import require_admin
from ..db import intake_col
from ..models import IntakeQuestion
# app/routers/admin_intake.py (add these imports near the top)
from pydantic import BaseModel
from typing import List
from pymongo import UpdateOne

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
