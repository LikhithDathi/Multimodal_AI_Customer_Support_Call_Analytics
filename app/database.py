import sqlite3

DB_PATH = "data/support_calls.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS support_calls")

    cursor.execute("""
    CREATE TABLE support_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audio_path TEXT,
        transcript TEXT,
        sentiment TEXT,
        issue_category TEXT,
        urgency TEXT,
        agent_behavior TEXT,
        call_outcome TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def insert_call(audio_path, transcript, insights):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO support_calls
        (audio_path, transcript, sentiment, issue_category, urgency, agent_behavior, call_outcome)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        audio_path,
        transcript,
        insights["sentiment"],
        insights["issue_category"],
        insights["urgency"],
        insights["agent_behavior"],
        insights["call_outcome"]
    ))

    conn.commit()
    conn.close()



def fetch_all_calls():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, audio_path, transcript, sentiment, issue_category, urgency, agent_behavior, call_outcome, created_at
        FROM support_calls
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def fetch_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT sentiment, COUNT(*) FROM support_calls GROUP BY sentiment")
    sentiment = dict(cursor.fetchall())

    cursor.execute("SELECT urgency, COUNT(*) FROM support_calls GROUP BY urgency")
    urgency = dict(cursor.fetchall())

    cursor.execute("SELECT call_outcome, COUNT(*) FROM support_calls GROUP BY call_outcome")
    outcome = dict(cursor.fetchall())

    conn.close()

    return {
        "sentiment_distribution": sentiment,
        "urgency_distribution": urgency,
        "call_outcome_distribution": outcome
    }

