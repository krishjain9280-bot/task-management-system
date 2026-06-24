"""
database.py
------------
Handles the SQLite connection lifecycle and automatic schema creation.

Design notes:
- We use Python's built-in `sqlite3` module (no ORM) so the SQL is fully
  explicit and easy to audit - good for a learning / production-ready
  reference project.
- `get_db()` returns a connection stored on Flask's `g` object so the
  same connection is reused for the duration of a single request.
- `init_app(app)` registers a teardown handler that closes the
  connection at the end of every request, and creates the tables
  (from schema.sql) the first time the app starts.
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """Return a SQLite connection for the current request, creating one
    if it does not exist yet."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_PATH"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # Rows behave like dicts: row["column_name"]
        g.db.row_factory = sqlite3.Row
        # Enforce foreign key constraints (off by default in SQLite)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create the instance/ folder and all tables (if they do not exist
    yet) using schema.sql. Safe to call every time the app starts."""
    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def init_app(app):
    """Wire database helpers into the Flask app."""
    init_db(app)
    app.teardown_appcontext(close_db)
