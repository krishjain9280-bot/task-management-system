"""
routes/auth_routes.py
----------------------
Authentication REST APIs:
    POST /api/signup   - create a new user account
    POST /api/login    - authenticate and start a session
    POST /api/logout   - end the session

Passwords are hashed with werkzeug.security (PBKDF2-SHA256 under the
hood) - plain text passwords are never stored or logged.
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from utils.helpers import is_valid_email, is_valid_username, log_activity

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or request.form
    full_name = (data.get("full_name") or "").strip()
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    # ---- Server-side validation ----
    errors = {}
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters."
    if not is_valid_username(username):
        errors["username"] = "Username must be 3-30 characters (letters, numbers, _ or .)."
    if not is_valid_email(email):
        errors["email"] = "Please provide a valid email address."
    if len(password) < 6:
        errors["password"] = "Password must be at least 6 characters."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
    ).fetchone()
    if existing:
        return jsonify({
            "success": False,
            "message": "An account with that username or email already exists."
        }), 409

    password_hash = generate_password_hash(password)
    cursor = db.execute(
        "INSERT INTO users (username, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
        (username, email, full_name, password_hash),
    )
    db.commit()
    user_id = cursor.lastrowid
    log_activity(user_id, "ACCOUNT_CREATED", f"User '{username}' signed up.")

    return jsonify({"success": True, "message": "Account created successfully. Please log in."}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    identifier = (data.get("username") or "").strip()  # username OR email
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"success": False, "message": "Username/email and password are required."}), 400

    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier.lower())
    ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid username/email or password."}), 401

    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user["full_name"]

    log_activity(user["id"], "LOGIN", f"User '{user['username']}' logged in.")

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['full_name']}!",
        "user": {"id": user["id"], "username": user["username"], "full_name": user["full_name"]}
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    user_id = session.get("user_id")
    username = session.get("username")
    if user_id:
        log_activity(user_id, "LOGOUT", f"User '{username}' logged out.")
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."}), 200
