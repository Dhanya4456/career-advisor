from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db, new_id, public_document, utc_now
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import RoadmapRequest, RoadmapResponse
from app.services.gemini import generate_roadmap

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])


@router.post(
    "/generate",
    response_model=RoadmapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a month-wise learning roadmap",
)
async def generate(
    body: RoadmapRequest,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    profile_dict = {
        "skills": current_user.skills or [],
        "degree": current_user.degree,
        "department": current_user.department,
    }

    ai_data = await generate_roadmap(
        profile_dict,
        body.target_role,
        body.duration_months,
        body.additional_context or "",
    )

    roadmap = {
        "id": new_id(), "user_id": current_user.user_id,
        "target_role": body.target_role, "duration_months": body.duration_months,
        "monthly_plan": ai_data.get("monthly_plan", []),
        "certifications": ai_data.get("certifications", []),
        "projects": ai_data.get("projects", []),
        "total_skills_to_learn": ai_data.get("total_skills_to_learn"),
        "raw_response": str(ai_data), "created_at": utc_now(),
    }
    await db.learning_roadmaps.insert_one(roadmap)
    return roadmap


@router.get(
    "/roadmaps",
    response_model=list[RoadmapResponse],
    summary="List all roadmaps for current user",
)
async def list_roadmaps(
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    rows = await db.learning_roadmaps.find({"user_id": current_user.user_id}).sort("created_at", -1).to_list(length=None)
    return [public_document(row) for row in rows]


@router.get(
    "/roadmaps/{roadmap_id}",
    response_model=RoadmapResponse,
    summary="Get a specific roadmap",
)
async def get_roadmap(
    roadmap_id: str,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    roadmap = public_document(await db.learning_roadmaps.find_one({"id": roadmap_id, "user_id": current_user.user_id}))
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


@router.delete("/roadmaps/{roadmap_id}", summary="Delete a roadmap")
async def delete_roadmap(
    roadmap_id: str,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    roadmap = await db.learning_roadmaps.find_one({"id": roadmap_id, "user_id": current_user.user_id})
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    await db.learning_roadmaps.delete_one({"id": roadmap_id, "user_id": current_user.user_id})
    return {"message": "Roadmap deleted", "success": True}
