"""
Database connection and initialization for SkillGap AI.
Uses SQLite - simple file-based database, perfect for a student project.
"""

import sqlite3
import os

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skillgap.db")


def get_db():
    """Open a connection to the SQLite database and return it."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name like a dict
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign key constraints
    return conn


def init_db():
    """
    Create all the tables if they don't exist yet.
    Run this once when the server starts.
    """
    conn = get_db()
    cursor = conn.cursor()

    # ── users ──────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── profiles ───────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL UNIQUE,
            education       TEXT,
            college         TEXT,
            current_year    TEXT,
            preferred_field TEXT,
            career_goal     TEXT,
            updated_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── resumes ────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            filename        TEXT,
            extracted_skills TEXT,   -- JSON list of skill names
            raw_text        TEXT,
            uploaded_at     TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── test_results ───────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            career_goal TEXT,
            score       INTEGER,
            total       INTEGER,
            answers     TEXT,   -- JSON: {question_id: chosen_option}
            taken_at    TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── skill_gaps ─────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gaps (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            career_goal     TEXT,
            current_skills  TEXT,   -- JSON list
            strong_skills   TEXT,   -- JSON list
            weak_skills     TEXT,   -- JSON list
            missing_skills  TEXT,   -- JSON list
            readiness_score REAL,
            created_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── roadmap_progress ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_progress (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            skill       TEXT    NOT NULL,
            status      TEXT    DEFAULT 'not_started',  -- not_started / in_progress / completed
            updated_at  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── analysis_history ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            career_goal     TEXT,
            resume_skills   TEXT,   -- JSON list
            strong_skills   TEXT,
            weak_skills     TEXT,
            missing_skills  TEXT,
            readiness_score REAL,
            test_score      INTEGER,
            test_total      INTEGER,
            created_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
