"""Skill assessment: serves the question bank and grades answers.

The correct answers never leave the server. Options are shuffled on every quiz
request, and answers are matched by option TEXT, so the order shown to the user
reveals nothing about the key.
"""
from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path

from app.database import public_document

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BASE_FILE = DATA_DIR / "skill_questions.json"            # 2 easy + 2 intermediate per skill
ADVANCED_FILE = DATA_DIR / "skill_questions_advanced.json"  # 3 advanced + 3 expert per skill

# (minimum %, code, label) -- bands from the question-bank document
LEVELS = ((75, "stronger", "Stronger understanding"), (50, "developing", "Developing"), (0, "needs_practice", "Needs practice"))


# How many questions of each difficulty a student at each experience level gets.
# Every quiz has 4 questions per skill; the mix (and therefore the questions) changes with the level.
COMPOSITION: dict[str, dict[str, int]] = {
    "student":   {"easy": 2, "intermediate": 2},
    "entry":     {"easy": 1, "intermediate": 1, "advanced": 2},
    "mid":       {"intermediate": 1, "advanced": 2, "expert": 1},
    "senior":    {"advanced": 3, "expert": 1},
    "executive": {"advanced": 1, "expert": 3},
}
LEVEL_LABELS = {
    "student": "Student",
    "entry": "Entry level",
    "mid": "Mid level",
    "senior": "Senior",
    "executive": "Executive",
}
TIER_ORDER = {"easy": 0, "intermediate": 1, "advanced": 2, "expert": 3}
QUESTIONS_PER_SKILL = 4


def normalize_experience(text: str | None) -> str:
    """Map the experience label chosen in the UI to a composition key (default: student)."""
    t = (text or "").strip().lower()
    for key in ("student", "entry", "mid", "senior", "exec"):
        if t.startswith(key):
            return "executive" if key == "exec" else key
    return "student"


@lru_cache
def _bank() -> dict[str, list[dict]]:
    """Merge every app/data/skill_questions*.json file (easy+intermediate, advanced+expert)."""
    files = sorted(DATA_DIR.glob("skill_questions*.json"))
    if not files:
        raise FileNotFoundError(f"No skill_questions*.json files found in {DATA_DIR}")
    merged: dict[str, dict[str, dict]] = {}
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{f.name} is not valid JSON ({exc}). Copy the file again from the update zip."
            ) from exc
        for skill, qs in data.items():
            bucket = merged.setdefault(skill, {})
            for q in qs:
                bucket.setdefault(q["id"], q)          # ids are unique; duplicates are ignored
    return {skill: list(items.values()) for skill, items in merged.items()}


def check_bank() -> str:
    """Raise ValueError if some skill lacks questions for any experience level; else return a summary."""
    needed = {tier: max((c.get(tier, 0) for c in COMPOSITION.values()), default=0) for tier in TIER_ORDER}
    problems: list[str] = []
    totals: dict[str, int] = {}
    for skill, qs in _bank().items():
        have: dict[str, int] = {}
        for q in qs:
            have[q["level"]] = have.get(q["level"], 0) + 1
            totals[q["level"]] = totals.get(q["level"], 0) + 1
        for tier, n in needed.items():
            if have.get(tier, 0) < n:
                problems.append(f"{skill}: {have.get(tier, 0)}/{n} {tier}")
    if problems:
        raise ValueError(
            "Skill question bank is incomplete (the quiz would repeat questions across experience "
            "levels): " + "; ".join(problems[:6]) + (" ..." if len(problems) > 6 else "")
        )
    summary = ", ".join(f"{t} {totals.get(t, 0)}" for t in TIER_ORDER)
    return f"Skill quiz bank OK: {len(_bank())} skills, {sum(totals.values())} questions ({summary})"


def _pick_questions(questions: list[dict], level: str) -> list[dict]:
    """Choose QUESTIONS_PER_SKILL questions for this level, easiest first."""
    by_tier: dict[str, list[dict]] = {}
    for q in questions:
        by_tier.setdefault(q["level"], []).append(q)
    picked: list[dict] = []
    for tier, count in COMPOSITION[level].items():
        pool = by_tier.get(tier, [])
        picked += random.sample(pool, min(count, len(pool)))
    if len(picked) < QUESTIONS_PER_SKILL:          # a tier is missing -> top up from the rest
        rest = [q for q in questions if q not in picked]
        picked += random.sample(rest, min(QUESTIONS_PER_SKILL - len(picked), len(rest)))
    return sorted(picked, key=lambda q: TIER_ORDER.get(q["level"], 9))


@lru_cache
def _index() -> dict[str, tuple[str, dict]]:
    return {q["id"]: (skill, q) for skill, qs in _bank().items() for q in qs}


def supported_skills() -> list[str]:
    return list(_bank())


def level_for(percentage: float) -> tuple[str, str]:
    for minimum, code, label in LEVELS:
        if percentage >= minimum:
            return code, label
    return LEVELS[-1][1], LEVELS[-1][2]


def build_quiz(skills: list[str], experience: str | None = None) -> tuple[list[dict], list[str], str]:
    """Return (quizzes, unsupported, level_label).

    The questions depend on the experience level. Skills without questions
    (e.g. custom ones) are skipped and reported as unsupported.
    """
    level = normalize_experience(experience)
    lookup = {name.lower(): name for name in _bank()}
    quizzes: list[dict] = []
    unsupported: list[str] = []
    seen: set[str] = set()
    for raw in skills:
        name = lookup.get((raw or "").strip().lower())
        if name is None:
            unsupported.append(raw)
            continue
        if name in seen:
            continue
        seen.add(name)
        questions = []
        for q in _pick_questions(_bank()[name], level):
            options = list(q["options"])
            random.shuffle(options)
            questions.append({"id": q["id"], "level": q["level"], "question": q["question"], "options": options})
        quizzes.append({"skill": name, "questions": questions})
    return quizzes, unsupported, LEVEL_LABELS[level]


def grade(answers: list[dict]) -> list[dict]:
    """Score answers per skill: percentage = correct / answered x 100."""
    tally: dict[str, dict] = {}
    counted: set[str] = set()
    for a in answers:
        qid = a.get("question_id")
        hit = _index().get(qid)
        if hit is None or qid in counted:
            continue
        counted.add(qid)
        skill, q = hit
        t = tally.setdefault(skill, {"correct": 0, "total": 0})
        t["total"] += 1
        if (a.get("answer") or "").strip() == q["answer"]:
            t["correct"] += 1
    results = []
    for skill in _bank():                      # keep the bank's order
        t = tally.get(skill)
        if not t:
            continue
        pct = round(100 * t["correct"] / t["total"])
        code, label = level_for(pct)
        results.append({"skill": skill, "correct": t["correct"], "total": t["total"],
                        "percentage": pct, "level": code, "label": label})
    return results


async def latest_results(db, user_id: str) -> list[dict]:
    """Most recent result for each skill the user has been assessed on."""
    rows = await db.skill_assessments.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
    latest: dict[str, dict] = {}
    for raw in rows:
        r = public_document(raw)
        if r["skill"] not in latest:
            latest[r["skill"]] = {"skill": r["skill"], "correct": r["correct"], "total": r["total"],
                                  "percentage": r["percentage"], "level": r["level"],
                                  "label": level_for(r["percentage"])[1]}
    return list(latest.values())
