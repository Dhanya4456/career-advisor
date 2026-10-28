from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db, new_id, utc_now
from app.middleware.auth import get_current_user
from app.models import UserProfile
from app.schemas import (
    AssessmentStartRequest,
    AssessmentStartResponse,
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
    SkillResult,
)
from app.services import assessment as svc

router = APIRouter(prefix="/assessment", tags=["Skill Assessment"])


@router.post(
    "/start",
    response_model=AssessmentStartResponse,
    summary="Get a skill quiz (answers are never included)",
)
async def start_quiz(
    body: AssessmentStartRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    quizzes, unsupported, level = svc.build_quiz(body.skills, body.experience)
    return {"quizzes": quizzes, "unsupported": unsupported, "experience_level": level}


@router.post(
    "/submit",
    response_model=AssessmentSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grade a quiz and save the results",
)
async def submit_quiz(
    body: AssessmentSubmitRequest,
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    results = svc.grade([a.model_dump() for a in body.answers])
    if not results:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid answers were submitted.",
        )
    for r in results:
        await db.skill_assessments.insert_one({
            "id": new_id(), "user_id": current_user.user_id,
            "skill": r["skill"], "correct": r["correct"], "total": r["total"],
            "percentage": r["percentage"], "level": r["level"], "created_at": utc_now(),
        })
    total = sum(r["total"] for r in results)
    overall = round(100 * sum(r["correct"] for r in results) / total)
    return {"results": results, "overall_percentage": overall}


@router.get(
    "/latest",
    response_model=list[SkillResult],
    summary="Latest result for every skill the user has been assessed on",
)
async def latest(
    db=Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    return await svc.latest_results(db, current_user.user_id)
