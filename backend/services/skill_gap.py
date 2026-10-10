"""
Skill Gap Analysis Service.

Given:
  - user's current skills (from resume)
  - user's test results (per skill)
  - selected career goal

Calculates:
  - strong skills
  - weak skills (in resume but performed poorly in test)
  - missing skills (required for goal but not in resume)
  - overall career readiness score
"""

import os
import csv

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")


def load_job_requirements() -> dict:
    """
    Load job role → required skills mapping from job_roles.csv.
    Returns: { "Machine Learning Engineer": ["Python", "Pandas", ...] }
    """
    requirements = {}
    job_csv = os.path.join(DATA_DIR, "job_roles.csv")
    with open(job_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            role = row["job_role"].strip()
            skills = [s.strip() for s in row["required_skills"].split(",")]
            requirements[role] = skills
    return requirements


def analyze_skill_gap(
    current_skills: list,
    career_goal: str,
    test_answers: dict,   # { question_id: chosen_option }
    questions: list       # list of question dicts from the test
) -> dict:
    """
    Core skill gap analysis function.

    Steps:
    1. Find required skills for the career goal
    2. Compare with current skills
    3. Use test results to classify skills as strong/weak
    4. Calculate readiness score
    """
    requirements = load_job_requirements()
    required_skills = requirements.get(career_goal, [])

    if not required_skills:
        # If career goal not found, use current skills
        required_skills = current_skills

    # Normalize to lowercase for comparison
    current_lower = [s.lower() for s in current_skills]

    # ── Step 1: Find missing skills ───────────────────────────────────────────
    missing_skills = [
        s for s in required_skills
        if s.lower() not in current_lower
    ]

    # ── Step 2: Find skills in resume that are also required ──────────────────
    matched_skills = [
        s for s in required_skills
        if s.lower() in current_lower
    ]

    # ── Step 3: Use test results to split matched into strong / weak ──────────
    # Build per-skill performance from test
    skill_performance = {}  # { skill: (correct, total) }
    for q in questions:
        skill = q.get("skill", "")
        q_id = str(q.get("id", ""))
        correct_ans = q.get("correct", "")
        chosen = test_answers.get(q_id, "")
        if skill not in skill_performance:
            skill_performance[skill] = {"correct": 0, "total": 0}
        skill_performance[skill]["total"] += 1
        if chosen == correct_ans:
            skill_performance[skill]["correct"] += 1

    strong_skills = []
    weak_skills = []

    for skill in matched_skills:
        # Check if we have test data for this skill
        perf = skill_performance.get(skill)
        if perf and perf["total"] > 0:
            accuracy = perf["correct"] / perf["total"]
            if accuracy >= 0.6:
                strong_skills.append(skill)
            else:
                weak_skills.append(skill)
        else:
            # No test question for this skill - assume strong if in resume
            strong_skills.append(skill)

    # ── Step 4: Calculate readiness score ─────────────────────────────────────
    # Formula (simple and explainable):
    # skill_coverage = matched_skills / required_skills  (40% weight)
    # test_score     = total correct / total questions    (60% weight)
    
    total_required = len(required_skills) if required_skills else 1
    skill_coverage = len(matched_skills) / total_required

    total_questions = sum(v["total"] for v in skill_performance.values())
    total_correct = sum(v["correct"] for v in skill_performance.values())
    test_score_ratio = (total_correct / total_questions) if total_questions > 0 else 0.5

    readiness_score = round((skill_coverage * 0.4 + test_score_ratio * 0.6) * 100, 1)

    # Assign priorities to missing skills (simple rule)
    missing_with_priority = []
    for skill in missing_skills:
        idx = required_skills.index(skill) if skill in required_skills else 999
        if idx < 3:
            priority = "High"
        elif idx < 6:
            priority = "Medium"
        else:
            priority = "Low"
        missing_with_priority.append({"skill": skill, "priority": priority})

    return {
        "career_goal": career_goal,
        "required_skills": required_skills,
        "current_skills": current_skills,
        "strong_skills": strong_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_with_priority,
        "readiness_score": readiness_score,
        "skill_coverage_pct": round(skill_coverage * 100, 1),
        "test_score_pct": round(test_score_ratio * 100, 1),
    }


def get_all_job_roles() -> list:
    """Return list of all available job role names."""
    requirements = load_job_requirements()
    return list(requirements.keys())
