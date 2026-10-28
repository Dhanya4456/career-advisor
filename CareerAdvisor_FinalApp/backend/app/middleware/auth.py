from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pymongo.errors import PyMongoError

from app.config import get_settings
from app.database import get_db
from app.models import UserProfile
from app.services.auth import JWT_ALGORITHM

settings = get_settings()
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
) -> UserProfile:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload: dict | None = None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise credentials_exception

    user_id = payload.get("sub") if payload else None
    if not user_id:
        raise credentials_exception

    try:
        document = await db.users.find_one({"user_id": user_id})
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    if document is None:
        raise credentials_exception
    return UserProfile.model_validate(document)
