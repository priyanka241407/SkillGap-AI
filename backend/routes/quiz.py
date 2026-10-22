"""
Practice Quiz routes.
Allows students to select skills/topics and difficulty levels,
attempt multiple-choice questions, view explanations, and save practice attempts.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db
from services.quiz_service import (
    get_quiz_topics,
    get_practice_questions,
    evaluate_practice_quiz,
)

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")


@quiz_bp.route("/topics", methods=["GET"])
@jwt_required()
def get_topics():
    """
    Return all supported practice quiz topics, difficulties,
    and a recommended topic based on the user's assessment/gap analysis.
    """
    user_id = get_jwt_identity()
    data = get_quiz_topics(user_id)
    return jsonify(data), 200


@quiz_bp.route("/questions", methods=["GET"])
@jwt_required()
def get_questions():
    """
    Get randomized practice questions for the chosen topic and difficulty.
    Query params: topic, difficulty, limit
    """
    topic = request.args.get("topic", "Python").strip()
    difficulty = request.args.get("difficulty", "All").strip()
    limit = int(request.args.get("limit", 5))

    if limit <= 0 or limit > 20:
        limit = 5

    questions = get_practice_questions(topic, difficulty, limit)
    return jsonify({
        "topic": topic,
        "difficulty": difficulty,
        "total": len(questions),
        "questions": questions,
    }), 200


@quiz_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_quiz():
    """
    Submit practice quiz answers, calculate score,
    return detailed explanations and store the attempt.
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    topic = data.get("topic", "General Practice").strip()
    difficulty = data.get("difficulty", "All").strip()
    answers = data.get("answers", {})

    if not answers:
        return jsonify({"error": "No answers were submitted."}), 400

    result = evaluate_practice_quiz(topic, difficulty, answers)

    # Save practice quiz attempt to database
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO assessment_attempts (
            user_id, assessment_type, skill_name, difficulty,
            total_questions, correct_answers, score_percentage, answers_detail
        ) VALUES (?, 'practice_quiz', ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            topic,
            difficulty,
            result["total"],
            result["score"],
            result["percentage"],
            json.dumps(result["results"]),
        )
    )
    attempt_id = cursor.lastrowid
    db.commit()
    db.close()

    result["attempt_id"] = attempt_id
    return jsonify(result), 200
