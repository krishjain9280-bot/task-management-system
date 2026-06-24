"""
utils/helpers.py
-----------------
Small reusable helper functions shared across route modules:
- generate_task_id(): produces the next auto-incrementing TA#### code
- log_activity(): writes a row into the activity_log table
- validation helpers for signup / task forms
"""

import re
from datetime import datetime
from flask import current_app
from database import get_db


def generate_task_id():
    """Generate the next human-friendly task identifier, e.g. TA1001,
    TA1002, TA1003 ...

    We look at the existing maximum numeric suffix among task_id values
    that match the configured prefix, then add 1. This avoids needing a
    separate counter table and self-heals even if rows are deleted.
    """
    db = get_db()
    prefix = current_app.config["TASK_ID_PREFIX"]
    start = current_app.config["TASK_ID_START"]

    rows = db.execute(
        "SELECT task_id FROM tasks WHERE task_id LIKE ?", (f"{prefix}%",)
    ).fetchall()

    max_num = start - 1
    for row in rows:
        match = re.match(rf"^{prefix}(\d+)$", row["task_id"])
        if match:
            max_num = max(max_num, int(match.group(1)))

    return f"{prefix}{max_num + 1}"


def log_activity(user_id, action, details=""):
    """Insert a row into the activity_log table."""
    db = get_db()
    db.execute(
        "INSERT INTO activity_log (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, action, details, datetime.utcnow().isoformat(sep=" ", timespec="seconds")),
    )
    db.commit()


def is_valid_email(email):
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email or ""))


def is_valid_username(username):
    return bool(re.match(r"^[a-zA-Z0-9_.]{3,30}$", username or ""))


def now_str():
    return datetime.utcnow().isoformat(sep=" ", timespec="seconds")
