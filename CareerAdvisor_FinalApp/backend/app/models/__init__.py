from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    user_id: str
    email: str
    full_name: str | None = None
    degree: str | None = None
    department: str | None = None
    cgpa: float | None = None
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    career_goals: str | None = None
    years_of_experience: int = 0
    linkedin_url: str | None = None
    github_url: str | None = None
    is_profile_complete: bool = False
    created_at: datetime
    updated_at: datetime
