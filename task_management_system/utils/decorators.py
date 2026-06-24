"""
utils/decorators.py
--------------------
Authentication-related decorators used to protect routes.
"""

from functools import wraps
from flask import session, redirect, url_for, jsonify, request


def login_required(view_func):
    """Protects a PAGE route. Redirects to the login page if the user
    is not authenticated."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("pages.login_page"))
        return view_func(*args, **kwargs)

    return wrapped


def api_login_required(view_func):
    """Protects an API/JSON route. Returns a 401 JSON error instead of
    redirecting, since the caller is JavaScript, not a browser navigation."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Authentication required. Please log in."}), 401
        return view_func(*args, **kwargs)

    return wrapped


def current_user_id():
    return session.get("user_id")


def current_username():
    return session.get("username")
