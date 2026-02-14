import sqlite3
from contextlib import contextmanager

DB_PATH = "data/support_calls.db"


# -----------------------------
# Connection handling
# -----------------------------
@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# -----------------------------
# Init DB
# -----------------------------
def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Deduplication
            file_hash TEXT UNIQUE,

            -- Core
            transcript TEXT,

            -- Analysis
            sentiment TEXT CHECK(sentiment IN ('positive', 'neutral', 'negative')),
            issue_category TEXT,
            urgency TEXT CHECK(urgency IN ('low', 'medium', 'high')),
            agent_behavior TEXT CHECK(agent_behavior IN ('polite', 'neutral', 'rude', 'unknown')),
            call_outcome TEXT CHECK(call_outcome IN ('resolved', 'unresolved')),

            -- Metadata
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON support_calls(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_outcome ON support_calls(call_outcome)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sentiment ON support_calls(sentiment)"
        )

        conn.commit()


# -----------------------------
# Duplicate check
# -----------------------------
def call_exists(file_hash: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM support_calls WHERE file_hash = ?",
            (file_hash,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# -----------------------------
# Insert call
# -----------------------------
def insert_call(file_hash, transcript, insights):
    """
    Insert a call analysis into the database.

    - Handles multi-label issue_category safely
    - Defensively normalizes data
    """

    # ✅ Normalize issue_category HERE (correct place)
    issue_category = insights.get("issue_category", ["other"])
    if isinstance(issue_category, list):
        issue_category = ",".join(issue_category)
    elif isinstance(issue_category, str):
        issue_category = issue_category
    else:
        issue_category = "other"

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO support_calls (
                    file_hash,
                    transcript,
                    sentiment,
                    issue_category,
                    urgency,
                    agent_behavior,
                    call_outcome
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                file_hash,
                transcript,
                insights.get("sentiment"),
                issue_category,
                insights.get("urgency"),
                insights.get("agent_behavior"),
                insights.get("call_outcome"),
            ))
            conn.commit()
            return {"inserted": True, "id": cursor.lastrowid}

    except sqlite3.IntegrityError:
        return {"inserted": False, "reason": "duplicate"}

    except Exception as e:
        return {"inserted": False, "reason": "db_error", "error": str(e)}


# -----------------------------
# Fetch calls
# -----------------------------
def fetch_all_calls():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    id,
                    transcript,
                    sentiment,
                    issue_category,
                    urgency,
                    agent_behavior,
                    call_outcome,
                    REPLACE(created_at, ' ', 'T') || 'Z' as created_at
                FROM support_calls
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return []
        raise


# -----------------------------
# Summary
# -----------------------------
def fetch_summary():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT sentiment, COUNT(*) FROM support_calls GROUP BY sentiment"
            )
            sentiment = dict(cursor.fetchall())

            cursor.execute(
                "SELECT urgency, COUNT(*) FROM support_calls GROUP BY urgency"
            )
            urgency = dict(cursor.fetchall())

            cursor.execute(
                "SELECT call_outcome, COUNT(*) FROM support_calls GROUP BY call_outcome"
            )
            outcome = dict(cursor.fetchall())

            return {
                "sentiment_distribution": sentiment,
                "urgency_distribution": urgency,
                "call_outcome_distribution": outcome
            }
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return {
                "sentiment_distribution": {},
                "urgency_distribution": {},
                "call_outcome_distribution": {}
            }
        raise


# -----------------------------
# Delete
# -----------------------------
def delete_call_by_id(call_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM support_calls WHERE id = ?",
            (call_id,)
        )
        conn.commit()
        return cursor.rowcount  # number of rows deleted


