"""
    config.py
    ---------
    Central configuration for the Flask application.
    Reads sensitive values from environment variables where possible,
    falling back to sane development defaults.
    """

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
        # Secret key used to sign session cookies. In production, ALWAYS
        # set this via an environment variable.
        SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

        # SQLite database file lives inside the instance/ folder.
        DATABASE_PATH = os.path.join(BASE_DIR, "instance", "taskmanager.db")

        # Session cookie lifetime (in seconds) - 7 days
        PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7

        # Pagination defaults for the task list API
        DEFAULT_PAGE_SIZE = 8

        # Prefix used for human-friendly auto generated Task IDs (TA1001, TA1002, ...)
        TASK_ID_PREFIX = "TA"
        TASK_ID_START = 1001
