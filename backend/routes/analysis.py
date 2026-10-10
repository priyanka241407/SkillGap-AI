"""
Skill gap, recommendations, and roadmap routes.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db
from services.skill_gap import analyze_skill_gap, get_all_job_roles
from services.recommender import get_recommendations, get_all_courses_filtered
from services.roadmap import generate_roadmap
from services.test_service import evaluate_test

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")


@analysis_bp.route("/job-roles", methods=["GET"])
def get_job_roles():
    """Public endpoint: return list of all supported job roles."""
    return jsonify({"roles": get_all_job_roles()}), 200


@analysis_bp.route("/run", methods=["POST"])
@jwt_required()
def run_analysis():
    """
    Run full skill gap analysis for the logged-in user.
    Uses resume skills + most recent test + career goal.
    Saves results and history.
    """
    user_id = get_jwt_identity()
    db = get_db()

    # Get resume skills
    resume = db.execute(
        "SELECT extracted_skills FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    current_skills = json.loads(resume["extracted_skills"]) if resume and resume["extracted_skills"] else []

    # Get career goal
    profile = db.execute("SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    career_goal = profile["career_goal"] if profile and profile["career_goal"] else ""

    if not career_goal:
        db.close()
        return jsonify({"error": "Please set a career goal first."}), 400

    # Get most recent test answers
    test_row = db.execute(
        "SELECT answers FROM test_results WHERE user_id = ? ORDER BY taken_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    answers = json.loads(test_row["answers"]) if test_row and test_row["answers"] else {}

    # Re-evaluate to get questions with skill info
    from services.test_service import load_all_questions
    all_questions = load_all_questions()

    # Run the analysis
    gap_result = analyze_skill_gap(current_skills, career_goal, answers, all_questions)

    missing_skills = gap_result["missing_skills"]
    weak_skills = gap_result["weak_skills"]
    strong_skills = gap_result["strong_skills"]
    readiness = gap_result["readiness_score"]

    # Get test score info
    test_score = 0
    test_total = 0
    if test_row:
        evaluated = evaluate_test(answers)
        test_score = evaluated["score"]
        test_total = evaluated["total"]

    # Save skill gap
    db.execute("""
        INSERT INTO skill_gaps (user_id, career_goal, current_skills, strong_skills,
            weak_skills, missing_skills, readiness_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, career_goal,
        json.dumps(current_skills),
        json.dumps(strong_skills),
        json.dumps(weak_skills),
        json.dumps([m["skill"] if isinstance(m, dict) else m for m in missing_skills]),
        readiness
    ))

    # Save to history
    db.execute("""
        INSERT INTO analysis_history
            (user_id, career_goal, resume_skills, strong_skills, weak_skills,
             missing_skills, readiness_score, test_score, test_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, career_goal,
        json.dumps(current_skills),
        json.dumps(strong_skills),
        json.dumps(weak_skills),
        json.dumps([m["skill"] if isinstance(m, dict) else m for m in missing_skills]),
        readiness, test_score, test_total
    ))

    db.commit()
    db.close()

    # Generate recommendations and roadmap
    recommendations = get_recommendations(missing_skills, weak_skills, career_goal)
    roadmap = generate_roadmap(
        career_goal, current_skills, strong_skills, weak_skills,
        missing_skills, gap_result["required_skills"]
    )

    return jsonify({
        **gap_result,
        "recommendations": recommendations,
        "roadmap": roadmap,
        "test_score": test_score,
        "test_total": test_total,
    }), 200


@analysis_bp.route("/result", methods=["GET"])
@jwt_required()
def get_latest_result():
    """Get the most recent analysis result for the user."""
    user_id = get_jwt_identity()
    db = get_db()

    gap = db.execute(
        "SELECT * FROM skill_gaps WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    test_row = db.execute(
        "SELECT score, total FROM test_results WHERE user_id = ? ORDER BY taken_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    profile = db.execute("SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    db.close()

    if not gap:
        return jsonify({"message": "No analysis run yet."}), 200

    current_skills = json.loads(gap["current_skills"]) if gap["current_skills"] else []
    strong_skills = json.loads(gap["strong_skills"]) if gap["strong_skills"] else []
    weak_skills = json.loads(gap["weak_skills"]) if gap["weak_skills"] else []
    missing_raw = json.loads(gap["missing_skills"]) if gap["missing_skills"] else []
    # missing_raw is a list of skill name strings (stored simplified)
    missing_skills = [{"skill": s, "priority": "Medium"} for s in missing_raw]
    career_goal = gap["career_goal"] or ""

    from services.skill_gap import load_job_requirements
    required_skills = load_job_requirements().get(career_goal, [])
    recommendations = get_recommendations(missing_skills, weak_skills, career_goal)
    roadmap = generate_roadmap(career_goal, current_skills, strong_skills, weak_skills, missing_skills, required_skills)

    return jsonify({
        "career_goal": career_goal,
        "current_skills": current_skills,
        "strong_skills": strong_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "readiness_score": gap["readiness_score"],
        "required_skills": required_skills,
        "recommendations": recommendations,
        "roadmap": roadmap,
        "test_score": test_row["score"] if test_row else 0,
        "test_total": test_row["total"] if test_row else 0,
    }), 200


@analysis_bp.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations_route():
    """Get recommendations with optional filters."""
    skill = request.args.get("skill")
    platform = request.args.get("platform")
    level = request.args.get("level")
    courses = get_all_courses_filtered(skill, platform, level)
    return jsonify({"courses": courses}), 200


@analysis_bp.route("/roadmap/progress", methods=["POST"])
@jwt_required()
def update_progress():
    """Update roadmap progress for a skill."""
    user_id = get_jwt_identity()
    data = request.get_json()
    skill = data.get("skill", "")
    status = data.get("status", "not_started")

    if not skill:
        return jsonify({"error": "Skill is required."}), 400
    if status not in ["not_started", "in_progress", "completed"]:
        return jsonify({"error": "Invalid status."}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id FROM roadmap_progress WHERE user_id = ? AND skill = ?", (user_id, skill)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE roadmap_progress SET status = ?, updated_at = datetime('now') WHERE user_id = ? AND skill = ?",
            (status, user_id, skill)
        )
    else:
        db.execute(
            "INSERT INTO roadmap_progress (user_id, skill, status) VALUES (?, ?, ?)",
            (user_id, skill, status)
        )
    db.commit()
    db.close()
    return jsonify({"message": "Progress updated!", "skill": skill, "status": status}), 200


@analysis_bp.route("/roadmap/progress", methods=["GET"])
@jwt_required()
def get_progress():
    """Get all roadmap progress for the user."""
    user_id = get_jwt_identity()
    db = get_db()
    rows = db.execute(
        "SELECT skill, status, updated_at FROM roadmap_progress WHERE user_id = ?", (user_id,)
    ).fetchall()
    db.close()
    return jsonify({"progress": [dict(r) for r in rows]}), 200


@analysis_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    """Get the user's analysis history."""
    user_id = get_jwt_identity()
    db = get_db()
    rows = db.execute(
        "SELECT * FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    db.close()
    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "career_goal": row["career_goal"],
            "readiness_score": row["readiness_score"],
            "test_score": row["test_score"],
            "test_total": row["test_total"],
            "resume_skills": json.loads(row["resume_skills"]) if row["resume_skills"] else [],
            "strong_skills": json.loads(row["strong_skills"]) if row["strong_skills"] else [],
            "weak_skills": json.loads(row["weak_skills"]) if row["weak_skills"] else [],
            "missing_skills": json.loads(row["missing_skills"]) if row["missing_skills"] else [],
            "created_at": row["created_at"],
        })
    return jsonify({"history": history}), 200


@analysis_bp.route("/history/<int:history_id>", methods=["DELETE"])
@jwt_required()
def delete_history_item(history_id):
    """Delete a single analysis history item."""
    user_id = get_jwt_identity()
    db = get_db()
    result = db.execute(
        "DELETE FROM analysis_history WHERE id = ? AND user_id = ?",
        (history_id, user_id)
    )
    db.commit()
    deleted_count = result.rowcount
    db.close()
    if deleted_count == 0:
        return jsonify({"error": "History item not found."}), 404
    return jsonify({"message": "History item deleted successfully."}), 200


@analysis_bp.route("/history", methods=["DELETE"])
@jwt_required()
def clear_all_history():
    """Clear all analysis history for the user."""
    user_id = get_jwt_identity()
    db = get_db()
    db.execute("DELETE FROM analysis_history WHERE user_id = ?", (user_id,))
    db.commit()
    db.close()
    return jsonify({"message": "All history cleared successfully."}), 200


@analysis_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_dashboard():
    """Aggregate data for the dashboard."""
    user_id = get_jwt_identity()
    db = get_db()

    user = db.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
    profile = db.execute("SELECT career_goal FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
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
    progress_rows = db.execute(
        "SELECT skill, status FROM roadmap_progress WHERE user_id = ?", (user_id,)
    ).fetchall()
    history_count = db.execute(
        "SELECT COUNT(*) as cnt FROM analysis_history WHERE user_id = ?", (user_id,)
    ).fetchone()
    db.close()

    current_skills = json.loads(resume["extracted_skills"]) if resume and resume["extracted_skills"] else []
    progress_list = [dict(r) for r in progress_rows]
    completed_count = sum(1 for p in progress_list if p["status"] == "completed")
    in_progress_count = sum(1 for p in progress_list if p["status"] == "in_progress")
    total_progress = len(progress_list)
    learning_pct = round((completed_count / total_progress * 100) if total_progress > 0 else 0, 1)

    weak_skills = json.loads(gap["weak_skills"]) if gap and gap["weak_skills"] else []
    missing_raw = json.loads(gap["missing_skills"]) if gap and gap["missing_skills"] else []

    return jsonify({
        "user_name": user["name"] if user else "",
        "career_goal": profile["career_goal"] if profile and profile["career_goal"] else "",
        "readiness_score": gap["readiness_score"] if gap else 0,
        "skills_found": len(current_skills),
        "skills_to_improve": len(weak_skills) + len(missing_raw),
        "learning_progress": learning_pct,
        "completed_topics": completed_count,
        "in_progress_topics": in_progress_count,
        "test_score": test_row["score"] if test_row else 0,
        "test_total": test_row["total"] if test_row else 0,
        "current_skills": current_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_raw,
        "history_count": history_count["cnt"] if history_count else 0,
        "progress": progress_list,
    }), 200
