"""
routes/profile_routes.py
--------------------------
User profile REST APIs:
    GET  /api/profile           - get current user's profile + task stats
    PUT  /api/profile           - update full name / email
    PUT  /api/profile/password  - change password
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from utils.decorators import api_login_required
from utils.helpers import is_valid_email, log_activity

profile_bp = Blueprint("profile", __name__, url_prefix="/api")


@profile_bp.route("/profile", methods=["GET"])
@api_login_required
def get_profile():
    db = get_db()
    user = db.execute("SELECT id, username, email, full_name, created_at FROM users WHERE id = ?",
                       (session["user_id"],)).fetchone()

    owned_total = db.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE owner_id = ?",
                              (session["user_id"],)).fetchone()["cnt"]
    owned_completed = db.execute(
        "SELECT COUNT(*) AS cnt FROM tasks WHERE owner_id = ? AND status = 'Completed'",
        (session["user_id"],)
    ).fetchone()["cnt"]

    return jsonify({
        "success": True,
        "profile": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "owned_tasks": owned_total,
            "owned_completed": owned_completed,
        }
    }), 200


@profile_bp.route("/profile", methods=["PUT"])
@api_login_required
def update_profile():
    data = request.get_json(silent=True) or request.form
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    errors = {}
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name must be at least 2 characters."
    if not is_valid_email(email):
        errors["email"] = "Please provide a valid email address."

    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    db = get_db()
    duplicate = db.execute("SELECT id FROM users WHERE email = ? AND id != ?",
                            (email, session["user_id"])).fetchone()
    if duplicate:
        return jsonify({"success": False, "message": "That email is already in use by another account."}), 409

    db.execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?",
               (full_name, email, session["user_id"]))
    db.commit()
    session["full_name"] = full_name

    log_activity(session["user_id"], "PROFILE_UPDATED", "Updated profile information.")

    return jsonify({"success": True, "message": "Profile updated successfully."}), 200


@profile_bp.route("/profile/password", methods=["PUT"])
@api_login_required
def change_password():
    data = request.get_json(silent=True) or request.form
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    confirm_password = data.get("confirm_password") or ""

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if not check_password_hash(user["password_hash"], current_password):
        return jsonify({"success": False, "message": "Current password is incorrect."}), 401

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters."}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "New passwords do not match."}), 400

    db.execute("UPDATE users SET password_hash = ? WHERE id = ?",
               (generate_password_hash(new_password), session["user_id"]))
    db.commit()

    log_activity(session["user_id"], "PASSWORD_CHANGED", "Password was changed.")

    return jsonify({"success": True, "message": "Password changed successfully."}), 200
