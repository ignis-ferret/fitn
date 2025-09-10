# ingest_intake.py
# One-time importer for your intake file (no extension, pure Python dicts).
# Usage:
#   MONGODB_URI="mongodb://mongo:27017" DB_NAME="fitn" INTAKE_FILE="interview_data/intake" PURGE=1 python ingest_intake.py

import asyncio
import os

import motor.motor_asyncio

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "fitn")
INTAKE_FILE = os.getenv("INTAKE_FILE", "interview_data/intake")  # no extension is fine
PURGE = os.getenv("PURGE", "0") == "1"


def _load_namespace_from_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    ns: dict = {}
    exec(compile(code, path, "exec"), {}, ns)
    return ns


def _iter_questions(ns: dict) -> list[dict]:
    # Prefer canonical map
    if "all_questions" in ns and isinstance(ns["all_questions"], dict):
        sections = ns["all_questions"]
    else:
        # Fallback to any *questions dicts
        sections = {
            k[:-10]: ns[k]
            for k in ns.keys()
            if k.endswith("_questions") and isinstance(ns[k], dict)
        }

    out: list[dict] = []
    for _, sec in sections.items():
        section_name = sec.get("section", "")
        for q in sec.get("questions", []):
            doc = dict(q)
            doc["section"] = section_name
            # normalize optional
            if "optional" in doc and doc["optional"] is None:
                del doc["optional"]
            out.append(doc)
    return out


async def main():
    ns = _load_namespace_from_file(INTAKE_FILE)
    docs = _iter_questions(ns)
    if not docs:
        raise SystemExit("No questions parsed.")

    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    col = client[DB_NAME]["intake_questions"]
    await col.create_index("id", unique=True)

    if PURGE:
        await col.delete_many({})
        print("Purged existing intake_questions")

    ins = upd = 0
    for doc in docs:
        res = await col.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
        if res.matched_count:
            upd += 1
        elif res.upserted_id:
            ins += 1
    print(f"Done. inserted={ins} updated={upd} total={len(docs)}")


if __name__ == "__main__":
    asyncio.run(main())
