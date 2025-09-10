# app/routers/rewards.py
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from ..db import options_col, sel_col
from ..deps import get_user_by_id, require_uid_cookie
from ..models import RewardTree, SelectionPayload

router = APIRouter(prefix="/api")


@router.get("/options")
async def get_options():
    doc = await options_col.find_one({})
    if not doc:
        return {"groups": []}
    doc.pop("_id", None)
    return doc


@router.post("/selections")
async def post_selection(request: Request, payload: SelectionPayload):
    uid = require_uid_cookie(request)
    user = await get_user_by_id(uid)
    if not user:
        raise HTTPException(403, "Auth required")

    tree_doc = await options_col.find_one({})
    if not tree_doc:
        raise HTTPException(400, "Options not loaded")
    tree = RewardTree(**{k: v for k, v in tree_doc.items() if k != "_id"})

    # validate level1, level2
    lvl1_set = {g.code for g in tree.groups}
    for code in payload.level1_codes:
        if code not in lvl1_set:
            raise HTTPException(400, f"Invalid level1 code: {code}")

    lvl2_set = {cat.code for g in tree.groups for cat in g.categories}
    for code in payload.level2_codes:
        if code not in lvl2_set:
            raise HTTPException(400, f"Invalid level2 code: {code}")

    # validate level3 one-per item
    items_map: dict[str, set[str]] = {}
    for g in tree.groups:
        for cat in g.categories:
            for it in cat.items:
                items_map[it.code] = {v.code for v in it.variations}

    seen_items = set()
    for ch in payload.level3_choices:
        item_code = ch.get("item_code")
        var_code = ch.get("variant_code")
        if not item_code or not var_code:
            raise HTTPException(400, "Missing item_code/variant_code")
        if item_code not in items_map:
            raise HTTPException(400, f"Invalid item_code: {item_code}")
        if var_code not in items_map[item_code]:
            raise HTTPException(400, f"Variant not in item: {var_code}")
        if item_code in seen_items:
            raise HTTPException(400, f"Multiple variants for item {item_code}")
        seen_items.add(item_code)

    record = payload.dict()
    record["user_id"] = uid
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    await sel_col.update_one({"user_id": uid}, {"$set": record}, upsert=True)
    return {"ok": True}
