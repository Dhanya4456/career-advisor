import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient

from app.config import get_settings

log = logging.getLogger("uvicorn.error")

settings = get_settings()
client = AsyncMongoClient(
    settings.mongodb_uri,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
)
database = client[settings.mongodb_database]

_ready = False
_init_lock = asyncio.Lock()

DB_UNAVAILABLE_DETAIL = (
    "Database is unavailable. Check MONGODB_URI and that your IP is allowed under "
    "MongoDB Atlas > Network Access."
)


def is_database_ready() -> bool:
    return _ready


async def ensure_database() -> bool:
    """Connect and create indexes if that has not succeeded yet.

    Lets the API recover when MongoDB was unreachable at startup but is reachable later.
    """
    if _ready:
        return True
    async with _init_lock:
        if _ready:
            return True
        try:
            await initialize_database()
        except Exception as exc:  # noqa: BLE001
            log.error("MongoDB connection failed: %s: %s", type(exc).__name__, str(exc)[:300])
            return False
    return True


async def get_db() -> AsyncGenerator:
    if not await ensure_database():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=DB_UNAVAILABLE_DETAIL)
    yield database


async def initialize_database() -> None:
    global _ready
    await client.admin.command("ping")
    await database.users.create_index([("email", ASCENDING)], unique=True)
    await database.users.create_index([("id", ASCENDING)], unique=True)
    await database.career_recommendations.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await database.resume_analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await database.skill_gap_analyses.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await database.learning_roadmaps.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    await database.chat_sessions.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])
    await database.skill_assessments.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    _ready = True


async def close_database() -> None:
    await client.close()


def new_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def public_document(document: dict | None) -> dict | None:
    if document is None:
        return None
    result = dict(document)
    result.pop("_id", None)
    return result
