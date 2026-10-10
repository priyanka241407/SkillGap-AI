"""
Authentication routes: register, login, logout.
Uses bcrypt for password hashing - never store plain text passwords.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
from database.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Create a new user account."""
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Basic validation
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    db = get_db()
    # Check if email already exists
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({"error": "An account with this email already exists."}), 409

    # Hash the password (bcrypt is industry standard)
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor = db.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hashed_pw)
    )
    user_id = cursor.lastrowid

    # Create an empty profile for the user
    db.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
    db.commit()
    db.close()

    # Create JWT token so they're logged in right after registration
    token = create_access_token(identity=str(user_id))
    return jsonify({
        "message": "Account created successfully!",
        "token": token,
        "user": {"id": user_id, "name": name, "email": email}
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login with email and password."""
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if not user:
        return jsonify({"error": "No account found with this email."}), 404

    # Check password
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Incorrect password."}), 401

    token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": {"id": user["id"], "name": user["name"], "email": user["email"]}
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get the currently logged-in user's info."""
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(dict(user)), 200
