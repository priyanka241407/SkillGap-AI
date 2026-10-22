"""
Skill Assessment History routes.
Provides comprehensive history of formal skill tests and practice quizzes,
trend data for progress charts, and detailed question-by-question review.
Strictly isolated by user_id.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db
from services.test_service import evaluate_test

assessment_bp = Blueprint("assessment", __name__, url_prefix="/api/assessment")


@assessment_bp.route("/history", methods=["GET"])
@jwt_required()
def get_assessment_history():
    """
    Retrieve all assessment attempts for the authenticated user with optional filtering.
    Query params:
      - type: 'all' (default), 'skill_test', 'practice_quiz'
      - skill: 'all' (default) or specific skill/topic
      - sort: 'newest' (default), 'oldest', 'highest', 'lowest'
    """
    user_id = get_jwt_identity()
    filter_type = request.args.get("type", "all").strip().lower()
    filter_skill = request.args.get("skill", "all").strip().lower()
    sort_by = request.args.get("sort", "newest").strip().lower()

    db = get_db()

    query = "SELECT * FROM assessment_attempts WHERE user_id = ?"
    params = [user_id]

    if filter_type in ["skill_test", "practice_quiz"]:
        query += " AND assessment_type = ?"
        params.append(filter_type)

    if filter_skill and filter_skill != "all":
        query += " AND LOWER(skill_name) LIKE ?"
        params.append(f"%{filter_skill}%")

    if sort_by == "oldest":
        query += " ORDER BY completed_at ASC"
    elif sort_by == "highest":
        query += " ORDER BY score_percentage DESC, completed_at DESC"
    elif sort_by == "lowest":
        query += " ORDER BY score_percentage ASC, completed_at DESC"
    else:  # newest
        query += " ORDER BY completed_at DESC"

    rows = db.execute(query, params).fetchall()

    attempts = []
    for r in rows:
        attempts.append({
            "id": r["id"],
            "assessment_type": r["assessment_type"],
            "skill_name": r["skill_name"],
            "difficulty": r["difficulty"] or "Standard",
            "total_questions": r["total_questions"],
            "correct_answers": r["correct_answers"],
            "score_percentage": r["score_percentage"],
            "completed_at": r["completed_at"],
            "has_details": bool(r["answers_detail"]),
        })

    # Chronological trend data (for progress chart)
    trend_rows = db.execute(
        "SELECT id, skill_name, assessment_type, score_percentage, completed_at "
        "FROM assessment_attempts WHERE user_id = ? ORDER BY completed_at ASC",
        (user_id,)
    ).fetchall()

    score_trend = []
    for tr in trend_rows:
        score_trend.append({
            "id": tr["id"],
            "skill_name": tr["skill_name"],
            "assessment_type": tr["assessment_type"],
            "score_percentage": tr["score_percentage"],
            "completed_at": tr["completed_at"],
        })

    # Available skills for filtering
    distinct_skills = db.execute(
        "SELECT DISTINCT skill_name FROM assessment_attempts WHERE user_id = ? ORDER BY skill_name ASC",
        (user_id,)
    ).fetchall()
    skill_options = [s["skill_name"] for s in distinct_skills if s["skill_name"]]

    db.close()

    total_attempts = len(score_trend)
    skill_test_count = sum(1 for a in score_trend if a["assessment_type"] == "skill_test")
    practice_quiz_count = sum(1 for a in score_trend if a["assessment_type"] == "practice_quiz")
    avg_score = round(sum(a["score_percentage"] for a in score_trend) / total_attempts, 1) if total_attempts > 0 else 0
    highest_score = max((a["score_percentage"] for a in score_trend), default=0)

    return jsonify({
        "attempts": attempts,
        "total_count": len(attempts),
        "skill_options": skill_options,
        "stats": {
            "total_assessments": total_attempts,
            "skill_tests_count": skill_test_count,
            "practice_quizzes_count": practice_quiz_count,
            "average_score": avg_score,
            "highest_score": highest_score,
            "score_trend": score_trend,
        }
    }), 200


@assessment_bp.route("/history/<int:attempt_id>", methods=["GET"])
@jwt_required()
def get_attempt_detail(attempt_id):
    """
    Retrieve full question-by-question breakdown for an assessment attempt.
    Includes question text, student's chosen option, correct option,
    and explanations.
    """
    user_id = get_jwt_identity()
    db = get_db()
    row = db.execute(
        "SELECT * FROM assessment_attempts WHERE id = ? AND user_id = ?",
        (attempt_id, user_id)
    ).fetchone()
    db.close()

    if not row:
        return jsonify({"error": "Assessment record not found."}), 404

    answers_raw = row["answers_detail"]
    questions_detail = []

    if answers_raw:
        try:
            parsed = json.loads(answers_raw)
            if isinstance(parsed, list):
                # Standard practice quiz or enriched test detail
                questions_detail = parsed
            elif isinstance(parsed, dict):
                # Legacy test answers map: { "q_id": "A" }
                evaluated = evaluate_test(parsed)
                questions_detail = evaluated.get("results", [])
        except Exception:
            questions_detail = []

    return jsonify({
        "id": row["id"],
        "assessment_type": row["assessment_type"],
        "skill_name": row["skill_name"],
        "difficulty": row["difficulty"] or "Standard",
        "total_questions": row["total_questions"],
        "correct_answers": row["correct_answers"],
        "score_percentage": row["score_percentage"],
        "completed_at": row["completed_at"],
        "questions_detail": questions_detail,
    }), 200


@assessment_bp.route("/history/<int:attempt_id>", methods=["DELETE"])
@jwt_required()
def delete_attempt(attempt_id):
    """Delete a single assessment record."""
    user_id = get_jwt_identity()
    db = get_db()
    res = db.execute(
        "DELETE FROM assessment_attempts WHERE id = ? AND user_id = ?",
        (attempt_id, user_id)
    )
    db.commit()
    deleted = res.rowcount
    db.close()

    if deleted == 0:
        return jsonify({"error": "Record not found."}), 404
    return jsonify({"message": "Assessment record deleted successfully."}), 200
