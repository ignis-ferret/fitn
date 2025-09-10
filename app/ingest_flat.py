# =========================
# ingest_flat.py — Flatten rewards tree into multiple collections
# =========================
# Usage:
#   python ingest_flat.py
# Env:
#   MONGODB_URI  (default: mongodb://mongo:27017)
#   DB_NAME      (default: fitn)
#   REWARDS_FILE (default: interview_data/rewards)  # path to the source text (e.g., /mnt/data/rew.txt)

import asyncio
import os
import re
from typing import List, Dict, Any

import motor.motor_asyncio
from models import Level1Group, Level2Category, Level3Item, RewardTree, Variation

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "fitn")
REWARDS_FILE = os.getenv("REWARDS_FILE", "interview_data/rewards")  # e.g., "/mnt/data/rew.txt"

# Lines like: 3.1 - X | 3.1.1 Y | 3.1.1.1 Z | 3.1.1.1.1 - “quote…”
re_level = re.compile(r"^\s*(\d+(?:\.\d+){0,4})\s*(?:-\s*)?(.*)$")
# Standalone example line (right after a variation code line)
re_variation_quote = re.compile(r'^\s*[–-]?\s*[“"](.+?)[”"]\s*$')


async def parse_tree() -> RewardTree:
    with open(REWARDS_FILE, "r", encoding="utf-8") as f:
        lines = [ln.rstrip() for ln in f]

    groups: List[Level1Group] = []
    g = None
    c = None
    i = None
    last_variation = None

    for ln in lines:
        m = re_level.match(ln)
        if not m:
            # possible next-line example text for the last variation
            if last_variation:
                qm = re_variation_quote.search(ln)
                if qm and not last_variation.example:
                    last_variation.example = qm.group(1).strip()
            continue

        code, rest = m.group(1), (m.group(2) or "").strip()
        parts = code.split(".")

        if len(parts) == 2:
            g = Level1Group(code=code, title=rest, categories=[])
            groups.append(g)
            c = None
            i = None
            last_variation = None

        elif len(parts) == 3:
            if not g:
                continue
            c = Level2Category(code=code, title=rest, items=[])
            g.categories.append(c)
            i = None
            last_variation = None

        elif len(parts) == 4:
            if not c:
                continue
            i = Level3Item(code=code, title=rest, variations=[])
            c.items.append(i)
            last_variation = None

        elif len(parts) == 5:
            if not i:
                continue
            # Inline example can be in rest as: '- “text”', '“text”', or plain text
            ex = ""
            qm = re_variation_quote.search(rest)
            if qm:
                ex = qm.group(1).strip()
            else:
                ex = rest.lstrip(" -–").strip(' “”"').strip()

            v = Variation(code=code, example=ex)
            i.variations.append(v)
            last_variation = v

    return RewardTree(groups=groups)


def flatten_tree(tree: RewardTree) -> Dict[str, List[Dict[str, Any]]]:
    groups_docs: List[Dict[str, Any]] = []
    categories_docs: List[Dict[str, Any]] = []
    items_docs: List[Dict[str, Any]] = []
    variations_docs: List[Dict[str, Any]] = []

    for g in tree.groups:
        groups_docs.append({
            "code": g.code,                 # e.g., "3.1"
            "title": g.title,               # e.g., "Food Treats"
        })

        for c in g.categories:
            categories_docs.append({
                "code": c.code,             # e.g., "3.1.1"
                "title": c.title,
                "group_code": g.code,
                "group_title": g.title,
            })

            for it in c.items:
                items_docs.append({
                    "code": it.code,         # e.g., "3.1.1.1"
                    "title": it.title,
                    "category_code": c.code,
                    "category_title": c.title,
                    "group_code": g.code,
                    "group_title": g.title,
                })

                for v in it.variations:
                    variations_docs.append({
                        "code": v.code,                     # e.g., "3.1.1.1.1"
                        "example": (v.example or "").strip(),
                        "item_code": it.code,
                        "item_title": it.title,
                        "category_code": c.code,
                        "category_title": c.title,
                        "group_code": g.code,
                        "group_title": g.title,
                        "active": True,
                    })

    return {
        "groups": groups_docs,
        "categories": categories_docs,
        "items": items_docs,
        "variations": variations_docs,
    }


async def upsert_collections(db, flat):
    col_groups = db["reward_groups"]
    col_categories = db["reward_categories"]
    col_items = db["reward_items"]
    col_variations = db["reward_variations"]

    # Reset collections
    await col_groups.delete_many({})
    await col_categories.delete_many({})
    await col_items.delete_many({})
    await col_variations.delete_many({})

    # Insert
    if flat["groups"]:
        await col_groups.insert_many(flat["groups"])
    if flat["categories"]:
        await col_categories.insert_many(flat["categories"])
    if flat["items"]:
        await col_items.insert_many(flat["items"])
    if flat["variations"]:
        await col_variations.insert_many(flat["variations"])

    # Indexes
    await col_groups.create_index([("code", 1)], unique=True)
    await col_categories.create_index([("code", 1)], unique=True)
    await col_categories.create_index([("group_code", 1)])
    await col_items.create_index([("code", 1)], unique=True)
    await col_items.create_index([("category_code", 1)])
    await col_items.create_index([("group_code", 1)])
    await col_variations.create_index([("code", 1)], unique=True)
    await col_variations.create_index([("item_code", 1)])
    await col_variations.create_index([("category_code", 1)])
    await col_variations.create_index([("group_code", 1)])
    # Text index for search across titles/examples
    await col_variations.create_index([
        ("example", "text"),
        ("item_title", "text"),
        ("category_title", "text"),
        ("group_title", "text"),
    ])

    # Counts
    g_cnt = await col_groups.estimated_document_count()
    c_cnt = await col_categories.estimated_document_count()
    i_cnt = await col_items.estimated_document_count()
    v_cnt = await col_variations.estimated_document_count()
    print(f"Inserted: groups={g_cnt}, categories={c_cnt}, items={i_cnt}, variations={v_cnt}")


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    tree = await parse_tree()
    flat = flatten_tree(tree)

    await upsert_collections(db, flat)
    print("Flattened ingest complete.")


if __name__ == "__main__":
    asyncio.run(main())
