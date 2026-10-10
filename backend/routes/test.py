"""
Test routes: get questions, submit answers.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db
from services.test_service import get_test_questions, evaluate_test

test_bp = Blueprint("test", __name__, url_prefix="/api/test")


@test_bp.route("/questions", methods=["GET"])
@jwt_required()
def get_questions():
    """
    Return test questions relevant to the user's skills and career goal.
    Frontend should call this after resume upload and career goal selection.
    """
    user_id = get_jwt_identity()
    db = get_db()

    # Get user's current skills from most recent resume
    resume = db.execute(
        "SELECT extracted_skills FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    # Get career goal from profile
    profile = db.execute(
        "SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)
    ).fetchone()

    db.close()

    user_skills = json.loads(resume["extracted_skills"]) if resume and resume["extracted_skills"] else []
    career_goal = profile["career_goal"] if profile and profile["career_goal"] else ""

    if not user_skills:
        return jsonify({"error": "Please upload your resume first."}), 400

    questions = get_test_questions(user_skills, career_goal, max_questions=10)
    return jsonify({"questions": questions, "total": len(questions)}), 200


@test_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_test():
    """
    Submit test answers and get results.
    Body: { "answers": { "question_id": "A" } }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    answers = data.get("answers", {})

    if not answers:
        return jsonify({"error": "No answers submitted."}), 400

    # Evaluate the test
    result = evaluate_test(answers)

    db = get_db()
    profile = db.execute("SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    career_goal = profile["career_goal"] if profile and profile["career_goal"] else ""

    # Save test result
    db.execute(
        """INSERT INTO test_results (user_id, career_goal, score, total, answers)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, career_goal, result["score"], result["total"], json.dumps(answers))
    )
    db.commit()
    db.close()

    return jsonify(result), 200


@test_bp.route("/results", methods=["GET"])
@jwt_required()
def get_test_results():
    """Get the user's most recent test results."""
    user_id = get_jwt_identity()
    db = get_db()
    result = db.execute(
        "SELECT * FROM test_results WHERE user_id = ? ORDER BY taken_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    db.close()

    if not result:
        return jsonify({"message": "No test taken yet."}), 200

    answers = json.loads(result["answers"]) if result["answers"] else {}
    evaluated = evaluate_test(answers)
    return jsonify(evaluated), 200
