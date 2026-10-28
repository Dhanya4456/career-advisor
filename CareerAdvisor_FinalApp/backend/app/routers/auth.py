from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import AuthResponse, LoginRequest, ProfileResponse, RegisterRequest
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(body: RegisterRequest, db=Depends(get_db)):
    result = await register_user(db, body.email, body.password, body.full_name)
    return AuthResponse(
        access_token=result["access_token"],
        user_id=result["user_id"],
        email=result["email"],
        full_name=result["full_name"],
    )


@router.post("/login", response_model=AuthResponse, summary="Login with email & password")
async def login(body: LoginRequest, db=Depends(get_db)):
    tokens = await login_user(db, body.email, body.password)
    return AuthResponse(
        access_token=tokens["access_token"],
        user_id=tokens["user_id"],
        email=tokens["email"],
        full_name=tokens["full_name"],
    )


@router.get("/me", response_model=ProfileResponse, summary="Get current authenticated user")
async def me(current_user: UserProfile = Depends(get_current_user)):
    return current_user
