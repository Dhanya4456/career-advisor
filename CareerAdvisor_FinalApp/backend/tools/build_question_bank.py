"""Convert PathAI_Complete_Skill_Questions.docx into app/data/skill_questions.json.

Usage (from the backend folder):
    pip install python-docx
    python tools/build_question_bank.py path/to/PathAI_Complete_Skill_Questions.docx

The script checks the document (40 skills x 4 questions, 4 options each, answer
key present) and stops with a clear message if anything is off.
"""
import json
import re
import sys
from pathlib import Path

from docx import Document

Q_RE = re.compile(r"^(\d+)\.\s*\[\s*([A-Za-z]+)\s*\|\s*([^\]]+?)\s*\]\s*(.+)$")
OPT_RE = re.compile(r"^([A-D])\.\s*(.+)$")
KEY_RE = re.compile(r"^(.+?):\s*((?:\d+-[A-D](?:,\s*)?)+)$")


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main(path: str) -> None:
    doc = Document(path)
    skills: dict[str, list[dict]] = {}
    key: dict[str, dict[int, str]] = {}
    current = None
    in_key = False

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name.lower() if p.style is not None else ""
        if style.startswith("heading 1"):
            if text.lower().startswith("answer key"):
                in_key, current = True, None
            elif text.lower() != "suggested scoring":
                in_key, current = False, text
                skills[current] = []
            continue
        if in_key:
            m = KEY_RE.match(text)
            if m:
                key[m.group(1).strip()] = {
                    int(n): l for n, l in re.findall(r"(\d+)-([A-D])", m.group(2))
                }
            continue
        if current is None:
            continue
        m = Q_RE.match(text)
        if m:
            num, level, topic, question = m.groups()
            skills[current].append(
                {"n": int(num), "level": level.lower(), "topic": topic.strip(),
                 "question": question.strip(), "options": []}
            )
            continue
        m = OPT_RE.match(text)
        if m and skills[current]:
            skills[current][-1]["options"].append(m.group(2).strip())

    problems = []
    bank = {}
    for skill, qs in skills.items():
        if len(qs) != 4:
            problems.append(f"{skill}: expected 4 questions, found {len(qs)}")
        if skill not in key:
            problems.append(f"{skill}: no answer key line")
            continue
        out = []
        for q in qs:
            if len(q["options"]) != 4:
                problems.append(f"{skill} Q{q['n']}: expected 4 options, found {len(q['options'])}")
                continue
            letter = key[skill].get(q["n"])
            if letter is None:
                problems.append(f"{skill} Q{q['n']}: no answer in key")
                continue
            out.append({
                "id": f"{slug(skill)}-{q['n']}",
                "level": q["level"],
                "topic": q["topic"],
                "question": q["question"],
                "options": q["options"],
                "answer": q["options"]["ABCD".index(letter)],   # stored as option TEXT
            })
        bank[skill] = out
    if len(bank) != 40:
        problems.append(f"expected 40 skills, found {len(bank)}")
    if problems:
        sys.exit("Question bank problems:\n  - " + "\n  - ".join(problems))

    target = Path(__file__).resolve().parent.parent / "app" / "data" / "skill_questions.json"
    target.write_text(json.dumps(bank, indent=1, ensure_ascii=False), encoding="utf-8")
    total = sum(len(v) for v in bank.values())
    print(f"OK: {len(bank)} skills, {total} questions -> {target}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
