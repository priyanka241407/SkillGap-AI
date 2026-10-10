"""
Resume routes: upload, extract skills, update skills.
"""

import os
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database.db import get_db
from services.skill_extractor import process_resume, extract_skills_from_text

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_resume():
    """
    Handle resume file upload.
    Saves the file, extracts text, identifies skills, stores in DB.
    """
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file provided. Please select a resume file."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX files are allowed."}), 400

    # Save file to uploads directory
    filename = secure_filename(f"user_{user_id}_{file.filename}")
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    # Process resume (extract text + skills)
    result = process_resume(file_path)
    skills = result["skills"]
    raw_text = result["raw_text"]

    # Save to database
    db = get_db()
    db.execute(
        """INSERT INTO resumes (user_id, filename, extracted_skills, raw_text)
           VALUES (?, ?, ?, ?)""",
        (user_id, filename, json.dumps(skills), raw_text[:1000])
    )
    db.commit()
    db.close()

    return jsonify({
        "message": "Resume uploaded and processed successfully!",
        "filename": file.filename,
        "skills": skills,
        "skills_count": len(skills),
        "raw_text_preview": raw_text[:200] if raw_text else ""
    }), 200


@resume_bp.route("/skills", methods=["GET"])
@jwt_required()
def get_skills():
    """Get the user's most recently extracted skills."""
    user_id = get_jwt_identity()
    db = get_db()
    resume = db.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    db.close()

    if not resume:
        return jsonify({"skills": [], "message": "No resume uploaded yet."}), 200

    skills = json.loads(resume["extracted_skills"]) if resume["extracted_skills"] else []
    return jsonify({
        "skills": skills,
        "filename": resume["filename"],
        "uploaded_at": resume["uploaded_at"]
    }), 200


@resume_bp.route("/skills", methods=["PUT"])
@jwt_required()
def update_skills():
    """Allow user to manually update their skill list."""
    user_id = get_jwt_identity()
    data = request.get_json()
    skills = data.get("skills", [])

    db = get_db()
    # Get the most recent resume
    resume = db.execute(
        "SELECT id FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    if resume:
        db.execute(
            "UPDATE resumes SET extracted_skills = ? WHERE id = ?",
            (json.dumps(skills), resume["id"])
        )
    else:
        # Create a resume record without a file
        db.execute(
            "INSERT INTO resumes (user_id, extracted_skills) VALUES (?, ?)",
            (user_id, json.dumps(skills))
        )

    db.commit()
    db.close()
    return jsonify({"message": "Skills updated!", "skills": skills}), 200
