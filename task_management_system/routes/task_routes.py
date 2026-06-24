"""
routes/task_routes.py
-----------------------
Task management REST APIs:
    GET    /api/tasks            - list tasks (search, filter, paginate)
    GET    /api/tasks/<task_id>  - get one task's full details
    POST   /api/tasks            - create a task (auto-generates Task ID)
    PUT    /api/tasks/<task_id>  - update a task
    DELETE /api/tasks/<task_id>  - delete a task
    GET    /api/dashboard/stats  - counts for the dashboard cards
    GET    /api/activity-log     - recent activity feed
"""

from flask import Blueprint, request, jsonify, session

from database import get_db
from utils.decorators import api_login_required
from utils.helpers import generate_task_id, log_activity, now_str

task_bp = Blueprint("tasks", __name__, url_prefix="/api")

VALID_STATUSES = ("Open", "In Progress", "Completed")


def serialize_task(row):
    return {
        "id": row["id"],
        "task_id": row["task_id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"],
        "owner_id": row["owner_id"],
        "owner_name": row["owner_name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# -------------------------------------------------------------------------
# GET /api/tasks  - list with search, status filter, and pagination
# -------------------------------------------------------------------------
@task_bp.route("/tasks", methods=["GET"])
@api_login_required
def list_tasks():
    db = get_db()

    search = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = max(1, min(100, int(request.args.get("per_page", 8))))
    except ValueError:
        page, per_page = 1, 8

    where_clauses = []
    params = []

    if search:
        where_clauses.append("(title LIKE ? OR task_id LIKE ? OR description LIKE ? OR owner_name LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like, like])

    if status and status in VALID_STATUSES:
        where_clauses.append("status = ?")
        params.append(status)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total = db.execute(f"SELECT COUNT(*) AS cnt FROM tasks {where_sql}", params).fetchone()["cnt"]

    offset = (page - 1) * per_page
    rows = db.execute(
        f"""SELECT * FROM tasks {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?""",
        params + [per_page, offset],
    ).fetchall()

    tasks = [serialize_task(r) for r in rows]
    total_pages = max(1, (total + per_page - 1) // per_page)

    return jsonify({
        "success": True,
        "tasks": tasks,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        }
    }), 200


# -------------------------------------------------------------------------
# GET /api/tasks/<task_id> - single task detail
# -------------------------------------------------------------------------
@task_bp.route("/tasks/<task_id>", methods=["GET"])
@api_login_required
def get_task(task_id):
    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if row is None:
        return jsonify({"success": False, "message": f"Task {task_id} was not found."}), 404
    return jsonify({"success": True, "task": serialize_task(row)}), 200


# -------------------------------------------------------------------------
# POST /api/tasks - create
# -------------------------------------------------------------------------
@task_bp.route("/tasks", methods=["POST"])
@api_login_required
def create_task():
    data = request.get_json(silent=True) or request.form

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    status = (data.get("status") or "Open").strip()
    owner_name = (data.get("owner_name") or "").strip()

    errors = {}
    if not title or len(title) < 3:
        errors["title"] = "Title must be at least 3 characters."
    if status not in VALID_STATUSES:
        errors["status"] = f"Status must be one of {', '.join(VALID_STATUSES)}."
    if not owner_name:
        errors["owner_name"] = "Owner is required."

    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    db = get_db()
    new_task_id = generate_task_id()
    timestamp = now_str()
    user_id = session["user_id"]

    db.execute(
        """INSERT INTO tasks
           (task_id, title, description, status, owner_id, owner_name, created_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (new_task_id, title, description, status, user_id, owner_name, user_id, timestamp, timestamp),
    )
    db.commit()

    log_activity(user_id, "TASK_CREATED", f"Created task {new_task_id} - '{title}'.")

    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (new_task_id,)).fetchone()
    return jsonify({"success": True, "message": f"Task {new_task_id} created.", "task": serialize_task(row)}), 201


# -------------------------------------------------------------------------
# PUT /api/tasks/<task_id> - update
# -------------------------------------------------------------------------
@task_bp.route("/tasks/<task_id>", methods=["PUT"])
@api_login_required
def update_task(task_id):
    db = get_db()
    existing = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if existing is None:
        return jsonify({"success": False, "message": f"Task {task_id} was not found."}), 404

    data = request.get_json(silent=True) or request.form

    title = (data.get("title") or existing["title"]).strip()
    description = data.get("description", existing["description"])
    status = (data.get("status") or existing["status"]).strip()
    owner_name = (data.get("owner_name") or existing["owner_name"]).strip()

    errors = {}
    if not title or len(title) < 3:
        errors["title"] = "Title must be at least 3 characters."
    if status not in VALID_STATUSES:
        errors["status"] = f"Status must be one of {', '.join(VALID_STATUSES)}."
    if not owner_name:
        errors["owner_name"] = "Owner is required."

    if errors:
        return jsonify({"success": False, "message": "Validation failed.", "errors": errors}), 400

    timestamp = now_str()
    db.execute(
        """UPDATE tasks
           SET title = ?, description = ?, status = ?, owner_name = ?, updated_at = ?
           WHERE task_id = ?""",
        (title, description, status, owner_name, timestamp, task_id),
    )
    db.commit()

    log_activity(session["user_id"], "TASK_UPDATED", f"Updated task {task_id} - '{title}'.")

    row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    return jsonify({"success": True, "message": f"Task {task_id} updated.", "task": serialize_task(row)}), 200


# -------------------------------------------------------------------------
# DELETE /api/tasks/<task_id>
# -------------------------------------------------------------------------
@task_bp.route("/tasks/<task_id>", methods=["DELETE"])
@api_login_required
def delete_task(task_id):
    db = get_db()
    existing = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if existing is None:
        return jsonify({"success": False, "message": f"Task {task_id} was not found."}), 404

    db.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    db.commit()

    log_activity(session["user_id"], "TASK_DELETED", f"Deleted task {task_id} - '{existing['title']}'.")

    return jsonify({"success": True, "message": f"Task {task_id} deleted."}), 200


# -------------------------------------------------------------------------
# GET /api/dashboard/stats - counts for dashboard cards
# -------------------------------------------------------------------------
@task_bp.route("/dashboard/stats", methods=["GET"])
@api_login_required
def dashboard_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) AS cnt FROM tasks").fetchone()["cnt"]
    open_count = db.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE status = 'Open'").fetchone()["cnt"]
    in_progress = db.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE status = 'In Progress'").fetchone()["cnt"]
    completed = db.execute("SELECT COUNT(*) AS cnt FROM tasks WHERE status = 'Completed'").fetchone()["cnt"]

    recent = db.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 5").fetchall()

    return jsonify({
        "success": True,
        "stats": {
            "total": total,
            "open": open_count,
            "in_progress": in_progress,
            "completed": completed,
        },
        "recent_tasks": [serialize_task(r) for r in recent],
    }), 200


# -------------------------------------------------------------------------
# GET /api/activity-log - recent activity feed (current user)
# -------------------------------------------------------------------------
@task_bp.route("/activity-log", methods=["GET"])
@api_login_required
def activity_log():
    db = get_db()
    limit = max(1, min(100, int(request.args.get("limit", 20))))
    rows = db.execute(
        """SELECT a.*, u.username FROM activity_log a
           JOIN users u ON u.id = a.user_id
           ORDER BY a.timestamp DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    logs = [
        {
            "id": r["id"],
            "action": r["action"],
            "details": r["details"],
            "timestamp": r["timestamp"],
            "username": r["username"],
        }
        for r in rows
    ]
    return jsonify({"success": True, "logs": logs}), 200
