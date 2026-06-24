"""
routes/page_routes.py
------------------------
Serves the actual HTML pages (server-rendered shells). The pages
themselves then call the JSON REST APIs (routes/auth_routes.py,
task_routes.py, profile_routes.py) via JavaScript (static/js/*.js) to
load and submit data dynamically.
"""

from flask import Blueprint, render_template, redirect, url_for, session

from utils.decorators import login_required

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_page"))
    return redirect(url_for("pages.login_page"))


@pages_bp.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_page"))
    return render_template("login.html")


@pages_bp.route("/signup")
def signup_page():
    if "user_id" in session:
        return redirect(url_for("pages.dashboard_page"))
    return render_template("signup.html")


@pages_bp.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", active="dashboard")


@pages_bp.route("/tasks")
@login_required
def tasks_page():
    return render_template("tasks.html", active="tasks")


@pages_bp.route("/tasks/new")
@login_required
def task_create_page():
    return render_template("task_create.html", active="tasks")


@pages_bp.route("/tasks/<task_id>")
@login_required
def task_detail_page(task_id):
    return render_template("task_detail.html", active="tasks", task_id=task_id)


@pages_bp.route("/profile")
@login_required
def profile_page():
    return render_template("profile.html", active="profile")
