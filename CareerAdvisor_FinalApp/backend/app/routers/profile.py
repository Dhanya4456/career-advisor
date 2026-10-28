from fastapi import APIRouter, Depends

from app.database import get_db, utc_now
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import MessageResponse, ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Student Profile"])


@router.get("", response_model=ProfileResponse, summary="Get current user profile")
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    return current_user


@router.put("", response_model=ProfileResponse, summary="Update user profile")
async def update_profile(
    body: ProfileUpdate,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    update_data = body.model_dump(exclude_none=True)
    profile = current_user.model_dump()
    profile.update(update_data)
    profile["is_profile_complete"] = all(
        [profile.get("full_name"), profile.get("degree"), profile.get("department"),
         profile.get("skills"), profile.get("career_goals")]
    )
    profile["updated_at"] = utc_now()
    await db.users.update_one({"user_id": current_user.user_id}, {"$set": profile})
    return UserProfile.model_validate(profile)


@router.delete("", response_model=MessageResponse, summary="Delete user profile")
async def delete_profile(
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    user_id = current_user.user_id
    await db.users.delete_one({"user_id": user_id})
    for collection in (
        db.career_recommendations, db.resume_analyses, db.skill_gap_analyses,
        db.learning_roadmaps, db.chat_sessions, db.skill_assessments,
    ):
        await collection.delete_many({"user_id": user_id})
    return MessageResponse(message="Profile deleted successfully")
