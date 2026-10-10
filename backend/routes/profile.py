"""
Profile routes: get and update user profile.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the logged-in user's profile."""
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    db.close()
    if not user:
        return jsonify({"error": "User not found."}), 404
    result = dict(user)
    if profile:
        result.update(dict(profile))
    return jsonify(result), 200


@profile_bp.route("/", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the logged-in user's profile."""
    user_id = get_jwt_identity()
    data = request.get_json()

    db = get_db()
    # Update name in users table if provided
    if "name" in data:
        db.execute("UPDATE users SET name = ? WHERE id = ?", (data["name"], user_id))

    # Upsert profile
    db.execute("""
        INSERT INTO profiles (user_id, education, college, current_year, preferred_field, career_goal, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            education = excluded.education,
            college = excluded.college,
            current_year = excluded.current_year,
            preferred_field = excluded.preferred_field,
            career_goal = excluded.career_goal,
            updated_at = excluded.updated_at
    """, (
        user_id,
        data.get("education", ""),
        data.get("college", ""),
        data.get("current_year", ""),
        data.get("preferred_field", ""),
        data.get("career_goal", ""),
    ))
    db.commit()
    db.close()
    return jsonify({"message": "Profile updated successfully!"}), 200
