
"""Async AI wrapper using the Google Gemini API."""
from __future__ import annotations

import asyncio
import json
import re

from fastapi import HTTPException
from google import genai
from google.genai import types

from app.config import get_settings

settings = get_settings()


def _extract_json(text: str) -> dict | list:
    """Strip markdown fences and parse JSON from AI output."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    return json.loads(clean)


_TIMEOUT_ERRORS = (asyncio.TimeoutError, TimeoutError)


async def generate(prompt: str, *, json_output: bool = False) -> str:
    """Generate a response using Gemini."""
    key = (settings.gemini_api_key or "").strip()

    if not key or key.lower().startswith(("your", "changeme", "xxx")):
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is missing or is a placeholder in backend/.env.",
        )

    timeout = settings.gemini_timeout_seconds
    client = genai.Client(
        api_key=key,
        http_options=types.HttpOptions(timeout=timeout * 1000),  # SDK timeout is in milliseconds
    )
    config = (
        types.GenerateContentConfig(response_mime_type="application/json")
        if json_output
        else None
    )
    for attempt in range(2):
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=settings.gemini_model,
                    contents=prompt,
                    config=config,
                ),
                timeout=timeout + 5,
            )

            content = response.text
            if not content:
                raise HTTPException(
                    status_code=502,
                    detail="Gemini returned an empty response (it may have been blocked by safety filters). Try rephrasing.",
                )
            return content

        except HTTPException:
            raise
        except Exception as exc:
            message = str(exc).lower()
            is_timeout = isinstance(exc, _TIMEOUT_ERRORS) or "timed out" in message or "timeout" in message
            is_quota = "429" in message or "quota" in message or "resource_exhausted" in message
            # Retry once only for short-lived server-side failures (not timeouts or quota,
            # which would just make the user wait longer).
            transient = not is_timeout and not is_quota and any(
                term in message for term in ("503", "unavailable", "overloaded", "temporar")
            )
            if transient and attempt == 0:
                await asyncio.sleep(1)
                continue

            if is_timeout:
                detail = f"Gemini request timed out after {timeout} seconds. Please try again."
            elif is_quota:
                detail = "Gemini quota or rate limit reached. Check your API usage and try again."
            elif "404" in message or "not_found" in message or "no longer available" in message:
                detail = (
                    f"Gemini model '{settings.gemini_model}' was not found or is no longer available. "
                    "Set GEMINI_MODEL in backend/.env to a current model (see ai.google.dev/gemini-api/docs/deprecations)."
                )
            elif "401" in message or "403" in message or "api key" in message or "permission_denied" in message:
                detail = "Gemini API key is invalid or API access is denied. Check GEMINI_API_KEY in backend/.env."
            else:
                detail = f"Gemini AI service error: {str(exc)[:200]}"

            raise HTTPException(status_code=502, detail=detail) from exc


async def _safe_generate(prompt: str) -> str:
    """Safely generate a response using Gemini."""
    return await generate(prompt)


async def generate_json(prompt: str) -> dict | list:
    """Generate and parse a JSON response."""
    raw = await generate(
        prompt
        + "\n\nReturn only valid JSON. Do not include markdown fences or explanations.",
        json_output=True,
    )

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned invalid JSON. Please try again.",
        ) from exc
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
        data = data[0]
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Gemini returned an unexpected response format. Please try again.")
    return data

# ── Domain helpers ────────────────────────────────────────────────────────────

async def get_career_recommendations(
    profile: dict, extra: str = "", skill_scores: list[dict] | None = None
) -> dict:
    assessment_text = "; ".join(
        f"{s['skill']} {s['percentage']}% ({s['label']})" for s in (skill_scores or [])
    )
    prompt = f"""
You are an expert career advisor. Analyze the student profile and generate detailed career recommendations.

Profile:
- Name: {profile.get('full_name', 'Student')}
- Degree: {profile.get('degree', 'N/A')}
- Department: {profile.get('department', 'N/A')}
- CGPA: {profile.get('cgpa', 'N/A')}
- Current Skills: {', '.join(profile.get('skills', []) or [])}
- Interests: {', '.join(profile.get('interests', []) or [])}
- Career Goals: {profile.get('career_goals', 'N/A')}
- Years of Experience: {profile.get('years_of_experience', 0)}
{f'- Additional Context: {extra}' if extra else ''}
{f'- Skill assessment results (short multiple-choice self-test, a rough signal only): {assessment_text}' if assessment_text else ''}

When assessment results are given, favour roles that build on the skills the student scored well in, and include skills with low scores as areas to strengthen in required_skills and the career_roadmap.

Return a JSON object with:
{{
  "recommended_roles": ["role1", "role2", "role3", "role4", "role5"],
  "required_skills": ["skill1", "skill2", ...],
  "salary_insights": [
    {{"role": "...", "min_salary": "$X", "max_salary": "$Y", "avg_salary": "$Z", "currency": "USD"}}
  ],
  "career_roadmap": {{
    "short_term": ["action1", ...],
    "mid_term": ["action1", ...],
    "long_term": ["action1", ...]
  }},
  "market_trends": ["trend1", "trend2", ...]
}}
"""
    return await generate_json(prompt)


async def analyze_resume(text: str, profile: dict, job_description: str) -> dict:
    prompt = f"""
You are an expert ATS resume reviewer and career consultant.

Resume Text:
{text[:6000]}

Candidate Profile:
- Degree: {profile.get('degree', 'N/A')}
- Department: {profile.get('department', 'N/A')}
- Target Goals: {profile.get('career_goals', 'N/A')}

Job Description:
{job_description[:6000]}

Perform a thorough ATS analysis and return a JSON object:
{{
  "ats_score": <float 0-100>,
  "extracted_skills": ["skill1", ...],
  "missing_skills": ["skill1", ...],
  "improvement_suggestions": ["suggestion1", ...],
  "strengths": ["strength1", ...],
  "weaknesses": ["weakness1", ...],
  "overall_feedback": "<2-3 sentence summary>"
}}

Be specific. ATS score should be calculated primarily based on how well the resume matches the provided Job Description. Consider:
- Matching skills and technologies
- Matching job-related keywords
- Relevant education and experience
- Required qualifications
- Resume formatting and ATS readability
- Missing important skills or keywords from the Job Description

The ATS score must represent the candidate's overall match to the provided Job Description, not just the quality of the resume.
"""
    return await generate_json(prompt)


async def analyze_skill_gap(profile: dict, target_role: str, extra: str = "") -> dict:
    current_skills = profile.get("skills", []) or []
    prompt = f"""
You are a technical skills expert. Perform a skill gap analysis.

Target Role: {target_role}
Current Skills: {', '.join(current_skills)}
Department: {profile.get('department', 'N/A')}
Experience: {profile.get('years_of_experience', 0)} years
{f'Context: {extra}' if extra else ''}

Return a JSON object:
{{
  "required_skills": ["skill1", ...],
  "missing_skills": ["skill1", ...],
  "matching_skills": ["skill1", ...],
  "gap_percentage": <float 0-100>,
  "priority_skills": ["most urgent skill1", ...],
  "estimated_timeline": "X months",
  "learning_resources": [
    {{"title": "...", "type": "course|book|tutorial|certification", "platform": "...", "url": "...", "duration": "..."}}
  ]
}}
"""
    return await generate_json(prompt)


async def generate_roadmap(profile: dict, target_role: str, months: int, extra: str = "") -> dict:
    prompt = f"""
You are a senior tech mentor creating a detailed, month-by-month learning roadmap.

Target Role: {target_role}
Duration: {months} months
Current Skills: {', '.join(profile.get('skills', []) or [])}
Background: {profile.get('degree', 'N/A')} in {profile.get('department', 'N/A')}
{f'Context: {extra}' if extra else ''}

Return a JSON object:
{{
  "monthly_plan": [
    {{
      "month": 1,
      "title": "Foundation",
      "skills": ["skill1", ...],
      "projects": ["project idea 1", ...],
      "resources": ["resource1", ...],
      "milestones": ["milestone1", ...]
    }}
  ],
  "certifications": [
    {{"name": "...", "provider": "...", "url": "...", "estimated_time": "..."}}
  ],
  "projects": [
    {{"name": "...", "description": "...", "skills_used": ["..."], "complexity": "beginner|intermediate|advanced"}}
  ],
  "total_skills_to_learn": <int>
}}

Include exactly {months} monthly_plan entries, numbered from 1 through {months}.
"""
    return await generate_json(prompt)


async def chat_with_advisor(
    user_message: str,
    history: list[dict],
    profile: dict,
) -> str:
    system = f"""You are an expert AI Career Advisor. You help students and professionals with:
- Career planning and exploration
- Skill development advice
- Resume and interview tips
- Job market insights
- Learning resource recommendations

User Profile Context:
- Name: {profile.get('full_name', 'User')}
- Degree: {profile.get('degree', 'N/A')} in {profile.get('department', 'N/A')}
- Skills: {', '.join(profile.get('skills', []) or [])}
- Career Goals: {profile.get('career_goals', 'N/A')}

Be concise, practical, and encouraging. Use bullet points when listing items."""

    # Build conversation history for context
    history_text = ""
    for msg in history[-10:]:  # last 10 messages for context window
        role = "User" if msg["role"] == "user" else "Advisor"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""{system}

Conversation History:
{history_text}
User: {user_message}
Advisor:"""

    return await _safe_generate(prompt)
