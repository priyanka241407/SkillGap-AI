"""
Test service.
Loads questions from questions.csv and selects relevant ones for the user's
skill set and career goal.
"""

import os
import csv
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")


def load_all_questions() -> list:
    """Load all questions from questions.csv."""
    questions = []
    q_csv = os.path.join(DATA_DIR, "questions.csv")
    with open(q_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                "id": int(row["id"]),
                "skill": row["skill"].strip(),
                "question": row["question"].strip(),
                "options": {
                    "A": row["option_a"].strip(),
                    "B": row["option_b"].strip(),
                    "C": row["option_c"].strip(),
                    "D": row["option_d"].strip(),
                },
                "correct": row["correct"].strip().upper(),
            })
    return questions


def get_test_questions(user_skills: list, career_goal: str, max_questions: int = 10) -> list:
    """
    Select test questions relevant to the user's skills and career goal.

    Strategy:
    - Get all questions for skills in the user's resume
    - Add questions for skills required by the career goal
    - Shuffle and limit to max_questions
    - Remove the correct answer from the returned data (so frontend can't cheat)
    """
    all_questions = load_all_questions()
    user_skills_lower = [s.lower() for s in user_skills]

    relevant = []
    for q in all_questions:
        if q["skill"].lower() in user_skills_lower:
            relevant.append(q)

    # Shuffle for variety
    random.shuffle(relevant)

    # Limit to max_questions
    selected = relevant[:max_questions]

    # Return questions without the correct answer (client doesn't need it for display)
    display_questions = []
    for q in selected:
        display_questions.append({
            "id": q["id"],
            "skill": q["skill"],
            "question": q["question"],
            "options": q["options"],
            # correct is NOT sent to frontend
        })

    return display_questions


def evaluate_test(answers: dict) -> dict:
    """
    Given user's answers { question_id: chosen_option }, evaluate the test.
    Returns score, total, and detailed results with correct answers.
    """
    all_questions = load_all_questions()
    # Build a lookup by id
    q_map = {str(q["id"]): q for q in all_questions}

    score = 0
    total = len(answers)
    results = []

    for q_id, chosen in answers.items():
        q = q_map.get(str(q_id))
        if not q:
            continue
        is_correct = chosen.upper() == q["correct"]
        if is_correct:
            score += 1
        results.append({
            "id": q["id"],
            "skill": q["skill"],
            "question": q["question"],
            "options": q["options"],
            "chosen": chosen.upper(),
            "correct": q["correct"],
            "is_correct": is_correct,
        })

    return {
        "score": score,
        "total": total,
        "percentage": round((score / total * 100) if total > 0 else 0, 1),
        "results": results,
    }
