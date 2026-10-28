from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db, new_id, public_document, utc_now
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import CareerRecommendationRequest, CareerRecommendationResponse
from app.services.assessment import latest_results
from app.services.gemini import get_career_recommendations

router = APIRouter(prefix="/career", tags=["Career Recommendations"])


@router.post(
    "/recommend",
    response_model=CareerRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI career recommendations",
)
async def recommend(
    body: CareerRecommendationRequest,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    if not current_user.skills and not current_user.degree:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please complete your profile with at least your degree and skills before generating recommendations.",
        )

    profile_dict = {
        "full_name": current_user.full_name,
        "degree": current_user.degree,
        "department": current_user.department,
        "cgpa": current_user.cgpa,
        "skills": current_user.skills or [],
        "interests": current_user.interests or [],
        "career_goals": current_user.career_goals,
        "years_of_experience": current_user.years_of_experience,
    }

    # Use the user's latest quiz results, limited to the skills currently selected
    selected = {s.lower() for s in (current_user.skills or [])}
    scores = [
        r for r in await latest_results(db, current_user.user_id)
        if r["skill"].lower() in selected
    ]

    ai_data = await get_career_recommendations(
        profile_dict, body.additional_context or "", scores
    )

    rec = {
        "id": new_id(),
        "user_id": current_user.user_id,
        "recommended_roles": ai_data.get("recommended_roles", []),
        "required_skills": ai_data.get("required_skills", []),
        "salary_insights": ai_data.get("salary_insights", {}),
        "career_roadmap": ai_data.get("career_roadmap", {}),
        "market_trends": ai_data.get("market_trends", []),
        "raw_response": str(ai_data),
        "created_at": utc_now(),
    }
    await db.career_recommendations.insert_one(rec)
    return rec


@router.get(
    "/recommendations",
    response_model=list[CareerRecommendationResponse],
    summary="List all career recommendations for current user",
)
async def list_recommendations(
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    rows = await db.career_recommendations.find({"user_id": current_user.user_id}).sort("created_at", -1).to_list(length=None)
    return [public_document(row) for row in rows]


@router.get(
    "/recommendations/{rec_id}",
    response_model=CareerRecommendationResponse,
    summary="Get a specific career recommendation",
)
async def get_recommendation(
    rec_id: str,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    rec = public_document(await db.career_recommendations.find_one({"id": rec_id, "user_id": current_user.user_id}))
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec
