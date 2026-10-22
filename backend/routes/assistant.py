"""
Career Assistant route: provides chat endpoint and suggestion prompts.
Uses rule-based AI guidance grounded in the user's existing profile,
skills, test results, and skill-gap analysis.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db
from services.career_assistant import generate_career_advice

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


def _get_user_context(user_id):
    """Retrieve all available user context without inventing data."""
    db = get_db()
    
    user = db.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
    profile = db.execute(
        "SELECT career_goal, preferred_field, education, college, current_year FROM profiles WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    resume = db.execute(
        "SELECT extracted_skills FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    test_row = db.execute(
        "SELECT score, total FROM test_results WHERE user_id = ? ORDER BY taken_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    gap = db.execute(
        "SELECT * FROM skill_gaps WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    
    db.close()

    current_skills = json.loads(resume["extracted_skills"]) if resume and resume["extracted_skills"] else []
    strong_skills = json.loads(gap["strong_skills"]) if gap and gap["strong_skills"] else []
    weak_skills = json.loads(gap["weak_skills"]) if gap and gap["weak_skills"] else []
    missing_skills = json.loads(gap["missing_skills"]) if gap and gap["missing_skills"] else []

    return {
        "user_name": user["name"] if user else "Student",
        "career_goal": profile["career_goal"] if profile and profile["career_goal"] else "",
        "preferred_field": profile["preferred_field"] if profile and profile["preferred_field"] else "",
        "education": profile["education"] if profile and profile["education"] else "",
        "college": profile["college"] if profile and profile["college"] else "",
        "current_skills": current_skills,
        "strong_skills": strong_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "readiness_score": gap["readiness_score"] if gap else None,
        "test_score": test_row["score"] if test_row else None,
        "test_total": test_row["total"] if test_row else None,
    }


@assistant_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    """Chat with the Career Assistant."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    user_context = _get_user_context(user_id)
    response_data = generate_career_advice(message, user_context)

    return jsonify(response_data), 200


@assistant_bp.route("/suggestions", methods=["GET"])
@jwt_required()
def get_suggestions():
    """Return useful suggested prompts for the user."""
    user_id = get_jwt_identity()
    user_context = _get_user_context(user_id)
    career_goal = user_context.get("career_goal")

    suggestions = [
        "What skills do I need to become a Data Analyst?",
        "How can I improve my Python skills?",
        "Create a beginner-friendly roadmap for a Machine Learning Engineer.",
        "Which projects should I add to my resume?",
        "How can I prepare for technical interviews?",
    ]

    if career_goal:
        suggestions.insert(0, f"What should I focus on next for my {career_goal} goal?")

    return jsonify({
        "suggestions": suggestions,
        "career_goal": career_goal,
        "readiness_score": user_context.get("readiness_score")
    }), 200
