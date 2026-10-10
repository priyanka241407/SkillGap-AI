"""
Recommendation service.
Matches missing/weak skills to courses in our local courses.csv.
"""

import os
import csv

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")


def load_courses() -> list:
    """Load all courses from courses.csv."""
    courses = []
    courses_csv = os.path.join(DATA_DIR, "courses.csv")
    with open(courses_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append({
                "id": int(row["id"]),
                "title": row["title"].strip(),
                "platform": row["platform"].strip(),
                "skill": row["skill"].strip(),
                "level": row["level"].strip(),
                "description": row["description"].strip(),
                "url": row["url"].strip(),
                "link_text": row["link_text"].strip(),
            })
    return courses


def get_recommendations(missing_skills: list, weak_skills: list, career_goal: str) -> list:
    """
    Returns a list of recommended courses.
    Priority: missing skills first, then weak skills.
    Each skill gets up to 2 recommendations.
    """
    all_courses = load_courses()
    recommended = []
    seen_ids = set()
    target_skills = []

    # Build ordered list: missing skills first, then weak skills
    for item in missing_skills:
        skill = item["skill"] if isinstance(item, dict) else item
        target_skills.append(skill)
    for skill in weak_skills:
        if skill not in target_skills:
            target_skills.append(skill)

    for skill in target_skills:
        skill_lower = skill.lower()
        count = 0
        for course in all_courses:
            if count >= 2:
                break
            if course["skill"].lower() == skill_lower and course["id"] not in seen_ids:
                course_copy = course.copy()
                course_copy["for_skill"] = skill
                course_copy["is_missing"] = skill in [
                    (m["skill"] if isinstance(m, dict) else m) for m in missing_skills
                ]
                recommended.append(course_copy)
                seen_ids.add(course["id"])
                count += 1

    return recommended


def get_all_courses_filtered(skill: str = None, platform: str = None, level: str = None) -> list:
    """Get courses with optional filters."""
    courses = load_courses()
    if skill:
        courses = [c for c in courses if skill.lower() in c["skill"].lower()]
    if platform:
        courses = [c for c in courses if platform.lower() in c["platform"].lower()]
    if level:
        courses = [c for c in courses if level.lower() == c["level"].lower()]
    return courses
