from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.config import get_settings
from app.database import new_id, utc_now

settings = get_settings()
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
JWT_ALGORITHM = "HS256"


def _token(user_id: str) -> str:
    expires = utc_now() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": user_id, "exp": expires}, settings.jwt_secret, algorithm=JWT_ALGORITHM)


async def register_user(db, email: str, password: str, full_name: str) -> dict:
    user_id = new_id()
    now = utc_now()
    document = {
        "id": user_id,
        "user_id": user_id,
        "email": email.lower(),
        "password_hash": password_context.hash(password),
        "full_name": full_name,
        "degree": None,
        "department": None,
        "cgpa": None,
        "skills": [],
        "interests": [],
        "career_goals": None,
        "years_of_experience": 0,
        "linkedin_url": None,
        "github_url": None,
        "is_profile_complete": False,
        "created_at": now,
        "updated_at": now,
    }
    try:
        await db.users.insert_one(document)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    return {"user_id": user_id, "email": document["email"], "full_name": full_name, "access_token": _token(user_id)}


async def login_user(db, email: str, password: str) -> dict:
    try:
        user = await db.users.find_one({"email": email.lower()})
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    if not user or not password_context.verify(password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {
        "access_token": _token(user["user_id"]),
        "user_id": user["user_id"],
        "email": user["email"],
        "full_name": user.get("full_name"),
    }
