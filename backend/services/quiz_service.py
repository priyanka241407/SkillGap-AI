"""
SkillGap AI - Practice Quiz Service
===================================
Provides topic-based and difficulty-based practice quizzes with
rich explanations, why-wrong explanations, and smart topic suggestions
grounded in the student's skill assessment / gap analysis results.
"""

import os
import random
import json
from services.test_service import load_all_questions
from database.db import get_db

TOPIC_CONFIG = {
    "Python": {
        "aliases": ["python"],
        "description": "Core syntax, data structures, OOP, list comprehensions, and generators.",
        "icon": "Code",
    },
    "SQL": {
        "aliases": ["sql", "database", "sqlite", "mysql", "postgresql"],
        "description": "Queries, filtering, joins, aggregates, window functions, and CTEs.",
        "icon": "Database",
    },
    "Machine Learning": {
        "aliases": ["machine learning", "ml", "scikit-learn", "deep learning"],
        "description": "Supervised/unsupervised learning, metrics, overfitting, and regularization.",
        "icon": "Brain",
    },
    "HTML and CSS": {
        "aliases": ["html and css", "html", "css", "web development"],
        "description": "Semantic markup, CSS box model, Flexbox, Grid, and responsive design.",
        "icon": "Layout",
    },
    "JavaScript": {
        "aliases": ["javascript", "js", "react", "node.js"],
        "description": "Variables, functions, closures, promises, event loop, and modern ES6+.",
        "icon": "FileCode",
    },
    "Data Analysis": {
        "aliases": ["data analysis", "pandas", "numpy", "statistics", "data visualization", "excel"],
        "description": "Descriptive statistics, Pandas, data wrangling, correlation, and EDA.",
        "icon": "BarChart",
    },
}


def _matches_topic(question_skill: str, topic_name: str) -> bool:
    """Check if a question's skill matches the selected topic or its aliases."""
    skill_lower = question_skill.strip().lower()
    topic_cfg = TOPIC_CONFIG.get(topic_name)
    if not topic_cfg:
        return skill_lower == topic_name.strip().lower()

    for alias in topic_cfg["aliases"]:
        if alias == skill_lower or alias in skill_lower or skill_lower in alias:
            return True
    return False


def get_quiz_topics(user_id=None):
    """
    Return all available practice topics with difficulty breakdown and question counts.
    If user_id is given, inspect their profile & skill gap results to recommend a practice topic.
    """
    all_questions = load_all_questions()

    topics = []
    for topic_name, cfg in TOPIC_CONFIG.items():
        matched = [q for q in all_questions if _matches_topic(q["skill"], topic_name)]
        difficulties = sorted(list(set(q.get("difficulty", "Beginner") for q in matched)))
        topics.append({
            "name": topic_name,
            "description": cfg["description"],
            "total_questions": len(matched),
            "difficulties": ["All"] + difficulties if difficulties else ["All"],
        })

    # Find a recommended topic for the student based on actual assessment/gap analysis
    suggested_topic = None
    if user_id:
        db = get_db()
        # 1. Check most recent skill gap
        gap = db.execute(
            "SELECT weak_skills, missing_skills, career_goal FROM skill_gaps WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        # 2. Check profile career goal if no gap yet
        profile = db.execute("SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        db.close()

        weak = json.loads(gap["weak_skills"]) if gap and gap["weak_skills"] else []
        missing = json.loads(gap["missing_skills"]) if gap and gap["missing_skills"] else []

        if weak:
            # Map weak skill to a topic
            for w in weak:
                for t_name in TOPIC_CONFIG:
                    if _matches_topic(w, t_name):
                        suggested_topic = {
                            "topic": t_name,
                            "reason": f"Recommended based on your recent skill test: strengthen your {w} proficiency.",
                        }
                        break
                if suggested_topic:
                    break

        if not suggested_topic and missing:
            # Map missing skill to a topic
            for m in missing:
                for t_name in TOPIC_CONFIG:
                    if _matches_topic(m, t_name):
                        suggested_topic = {
                            "topic": t_name,
                            "reason": f"Required for your career goal ({gap['career_goal'] if gap else 'your target role'}): start learning {m}.",
                        }
                        break
                if suggested_topic:
                    break

        if not suggested_topic:
            goal = (profile["career_goal"] if profile and profile["career_goal"] else "").lower()
            if "data" in goal:
                suggested_topic = {"topic": "Data Analysis", "reason": "Great starting point for Data careers."}
            elif "machine" in goal or "ai" in goal:
                suggested_topic = {"topic": "Machine Learning", "reason": "Core foundation for AI and ML roles."}
            elif "web" in goal or "full" in goal:
                suggested_topic = {"topic": "JavaScript", "reason": "Essential for modern Web Development."}

    if not suggested_topic:
        suggested_topic = {"topic": "Python", "reason": "Recommended starter topic for all technical roles."}

    return {
        "topics": topics,
        "suggested_topic": suggested_topic,
    }


def get_practice_questions(topic: str, difficulty: str = "All", limit: int = 5):
    """
    Select randomized questions for a practice quiz without revealing correct answers.
    """
    all_questions = load_all_questions()

    # Filter by topic
    matched = [q for q in all_questions if _matches_topic(q["skill"], topic)]

    # Filter by difficulty if specified
    if difficulty and difficulty.lower() != "all":
        diff_matched = [q for q in matched if q.get("difficulty", "").lower() == difficulty.lower()]
        if diff_matched:
            matched = diff_matched

    if not matched:
        # Fallback to general questions if specific topic has no direct match
        matched = all_questions

    random.shuffle(matched)
    selected = matched[:limit]

    # Return display-safe questions (stripping answers and explanations)
    display_questions = []
    for q in selected:
        display_questions.append({
            "id": q["id"],
            "skill": q["skill"],
            "difficulty": q.get("difficulty", "Beginner"),
            "question": q["question"],
            "options": q["options"],
        })

    return display_questions


def evaluate_practice_quiz(topic: str, difficulty: str, answers: dict):
    """
    Evaluate user's practice quiz answers, calculate score,
    and attach educational explanations and why-wrong notes for each question.
    """
    all_questions = load_all_questions()
    q_map = {str(q["id"]): q for q in all_questions}

    score = 0
    total = len(answers)
    detailed_results = []
    topics_to_practice = set()

    for q_id, chosen in answers.items():
        q = q_map.get(str(q_id))
        if not q:
            continue

        chosen_letter = str(chosen).strip().upper()
        correct_letter = q["correct"].strip().upper()
        is_correct = chosen_letter == correct_letter

        if is_correct:
            score += 1
        else:
            # Note topic/skill for practice recommendation
            topics_to_practice.add(f"{q.get('difficulty', '')} {q['skill']}".strip())

        chosen_text = q["options"].get(chosen_letter, chosen_letter)
        correct_text = q["options"].get(correct_letter, correct_letter)

        detailed_results.append({
            "id": q["id"],
            "skill": q["skill"],
            "difficulty": q.get("difficulty", "Beginner"),
            "question": q["question"],
            "options": q["options"],
            "chosen": chosen_letter,
            "chosen_text": chosen_text,
            "correct": correct_letter,
            "correct_text": correct_text,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "The selected option is correct based on technical standard practices."),
            "why_wrong": q.get("why_wrong", "The other options represent different concepts or invalid syntax.") if not is_correct else None,
        })

    percentage = round((score / total * 100) if total > 0 else 0, 1)

    return {
        "topic": topic,
        "difficulty": difficulty,
        "total": total,
        "score": score,
        "incorrect": total - score,
        "percentage": percentage,
        "topics_to_practice": sorted(list(topics_to_practice)),
        "results": detailed_results,
    }
