"""
routes/auth_routes.py
----------------------
Authentication REST APIs:
    POST /api/signup
    POST /api/login
    POST /api/logout

Passwords are hashed using werkzeug.security.
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from utils.helpers import is_valid_email, is_valid_username, log_activity

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


# ---------------- SIGNUP ----------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or request.form

    full_name = (data.get("full_name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    errors = {}

    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters."

    if not is_valid_username(username):
        errors["username"] = "Invalid username format."

    if not is_valid_email(email):
        errors["email"] = "Invalid email."

    if len(password) < 6:
        errors["password"] = "Password must be at least 6 characters."

    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    if errors:
        return jsonify({"success": False, "message": "Validation failed", "errors": errors}), 400

    db = get_db()

    existing = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email)
    ).fetchone()

    if existing:
        return jsonify({
            "success": False,
            "message": "User already exists"
        }), 409

    password_hash = generate_password_hash(password)

    cursor = db.execute(
        "INSERT INTO users (username, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
        (username, email, full_name, password_hash)
    )
    db.commit()

    user_id = cursor.lastrowid
    log_activity(user_id, "SIGNUP", f"User {username} created account")

    return jsonify({
        "success": True,
        "message": "Account created successfully"
    }), 201


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form

    identifier = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400
    print("LOGIN ATTEMPT:", identifier)
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (identifier, identifier.lower())
    ).fetchone()
    print("USER FOUND:", user)

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid login"}), 401

    session.clear()
    session.permanent = True

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user["full_name"]

    log_activity(user["id"], "LOGIN", f"{user['username']} logged in")

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"]
        }
    }), 200


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    user_id = session.get("user_id")

    session.clear()

    if user_id:
        try:
            log_activity(user_id, "LOGOUT", "User logged out")
        except:
            pass

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200