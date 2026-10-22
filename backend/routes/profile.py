"""
Profile routes: get and update user profile.
Supports the extended profile fields added in v2:
  branch, career_domain, experience_level, self_skills (JSON),
  weekly_hours, portfolio_url
All existing fields (education, college, current_year, preferred_field,
career_goal) are fully preserved.
"""

import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import get_db

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("/", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the logged-in user's profile including all extended fields."""
    user_id = get_jwt_identity()
    db = get_db()
    user    = db.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    profile = db.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    db.close()

    if not user:
        return jsonify({"error": "User not found."}), 404

    result = dict(user)
    if profile:
        p = dict(profile)
        # Parse self_skills JSON list safely
        raw_skills = p.get("self_skills") or "[]"
        try:
            p["self_skills"] = json.loads(raw_skills)
        except (json.JSONDecodeError, TypeError):
            p["self_skills"] = []
        result.update(p)
    else:
        # Provide defaults so the frontend always has expected keys
        result["self_skills"] = []

    return jsonify(result), 200


@profile_bp.route("/", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the logged-in user's profile (existing + extended fields)."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    db = get_db()

    # Update display name in users table
    if "name" in data and data["name"].strip():
        db.execute("UPDATE users SET name = ? WHERE id = ?",
                   (data["name"].strip(), user_id))

    # Serialize self_skills list to JSON for storage
    raw_skills = data.get("self_skills", [])
    if isinstance(raw_skills, list):
        skills_json = json.dumps(raw_skills)
    else:
        skills_json = "[]"

    # Upsert profile row (preserves existing rows, only adds/updates fields)
    db.execute("""
        INSERT INTO profiles (
            user_id, education, college, current_year, preferred_field, career_goal,
            branch, career_domain, experience_level, self_skills, weekly_hours,
            portfolio_url, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id) DO UPDATE SET
            education        = excluded.education,
            college          = excluded.college,
            current_year     = excluded.current_year,
            preferred_field  = excluded.preferred_field,
            career_goal      = excluded.career_goal,
            branch           = excluded.branch,
            career_domain    = excluded.career_domain,
            experience_level = excluded.experience_level,
            self_skills      = excluded.self_skills,
            weekly_hours     = excluded.weekly_hours,
            portfolio_url    = excluded.portfolio_url,
            updated_at       = excluded.updated_at
    """, (
        user_id,
        data.get("education", ""),
        data.get("college", ""),
        data.get("current_year", ""),
        data.get("preferred_field", ""),
        data.get("career_goal", ""),
        data.get("branch", ""),
        data.get("career_domain", ""),
        data.get("experience_level", ""),
        skills_json,
        data.get("weekly_hours", ""),
        data.get("portfolio_url", ""),
    ))

    db.commit()
    db.close()
    return jsonify({"message": "Profile updated successfully!"}), 200
