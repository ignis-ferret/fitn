# =========================
# 2) ingest.py (parse rew.txt → Mongo)
# =========================
# Usage: python ingest.py (ensure MONGODB_URI is set)
# ingest.py — fixes variation example capture (inline and next-line), keeps your DB/env

import asyncio
import os
import re

import motor.motor_asyncio
from models import Level1Group, Level2Category, Level3Item, RewardTree, Variation

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "fitn")  # <- set to your target DB

# Lines like: 3.1 - X | 3.1.1 Y | 3.1.1.1 Z | 3.1.1.1.1 - “quote…”
re_level = re.compile(r"^\s*(\d+(?:\.\d+){0,4})\s*(?:-\s*)?(.*)$")
# Standalone example line (right after a variation code line)
re_variation_quote = re.compile(r'^\s*[–-]?\s*[“"](.+?)[”"]\s*$')


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    col = db["reward_options"]

    with open("interview_data/rewards", "r", encoding="utf-8") as f:
        lines = [ln.rstrip() for ln in f]

    groups = []
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

    tree = RewardTree(groups=groups)
    await col.delete_many({})
    await col.insert_one(tree.dict())
    print("Ingested.")


if __name__ == "__main__":
    asyncio.run(main())
