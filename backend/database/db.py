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

    # ── assessment_attempts ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_attempts (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            assessment_type   TEXT    NOT NULL, -- 'skill_test' or 'practice_quiz'
            skill_name        TEXT    NOT NULL,
            difficulty        TEXT    DEFAULT 'All',
            total_questions   INTEGER NOT NULL,
            correct_answers   INTEGER NOT NULL,
            score_percentage  REAL    NOT NULL,
            answers_detail    TEXT,             -- JSON string of detailed results
            completed_at      TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Sync past tests from test_results into assessment_attempts if not already synced
    cursor.execute("SELECT COUNT(*) FROM assessment_attempts WHERE assessment_type = 'skill_test'")
    existing_synced = cursor.fetchone()[0]
    if existing_synced == 0:
        cursor.execute("SELECT id, user_id, career_goal, score, total, answers, taken_at FROM test_results")
        past_tests = cursor.fetchall()
        for t in past_tests:
            pct = round((t["score"] / t["total"] * 100) if t["total"] and t["total"] > 0 else 0, 1)
            cursor.execute("""
                INSERT INTO assessment_attempts (user_id, assessment_type, skill_name, difficulty, total_questions, correct_answers, score_percentage, answers_detail, completed_at)
                VALUES (?, 'skill_test', ?, 'Comprehensive', ?, ?, ?, ?, ?)
            """, (t["user_id"], t["career_goal"] or "Skill Assessment", t["total"] or 0, t["score"] or 0, pct, t["answers"], t["taken_at"]))

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
