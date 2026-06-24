-- =====================================================================
-- schema.sql
-- Database schema for the Task Management System (SQLite).
-- This file is executed automatically by database.py on first run,
-- but is also provided here so it can be inspected / run manually.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- USERS TABLE
-- Stores registered application users. Passwords are NEVER stored in
-- plain text - only a salted hash (see werkzeug.security in the app).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    full_name       TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------
-- TASKS TABLE
-- Stores all tasks. `task_id` is the human-friendly auto generated
-- identifier (TA1001, TA1002, ...) shown in the UI. `owner_id` /
-- `created_by` are foreign keys into the users table, establishing the
-- relationship between tasks and the users who own / created them.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id         TEXT UNIQUE NOT NULL,         -- e.g. TA1001
    title           TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'Open'  -- Open | In Progress | Completed
                        CHECK (status IN ('Open', 'In Progress', 'Completed')),
    owner_id        INTEGER NOT NULL,
    owner_name      TEXT NOT NULL,                -- denormalized for fast display
    created_by      INTEGER NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (owner_id)   REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- ACTIVITY LOG TABLE
-- Records every significant action (login, task created/updated/deleted,
-- profile updated, etc.) for the Activity Log feature.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    action      TEXT NOT NULL,
    details     TEXT,
    timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Helpful indexes for search / filter / pagination performance
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_owner    ON tasks (owner_id);
CREATE INDEX IF NOT EXISTS idx_activity_user  ON activity_log (user_id);
