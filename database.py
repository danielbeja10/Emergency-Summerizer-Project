import sqlite3
from config import DATABASE_PATH


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT    NOT NULL,
                source_type TEXT    NOT NULL CHECK(source_type IN ('text', 'pdf')),
                file_path   TEXT,
                summary     TEXT    NOT NULL,
                source_text TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            conn.execute("ALTER TABLE summaries ADD COLUMN source_text TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()


def save_summary(source_name: str, source_type: str, file_path: str | None,
                 summary: str, source_text: str | None = None) -> int:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO summaries (source_name, source_type, file_path, summary, source_text) VALUES (?, ?, ?, ?, ?)",
            (source_name, source_type, file_path, summary, source_text)
        )
        conn.commit()
        return cursor.lastrowid


def get_all_summaries() -> list:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM summaries ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_summary_by_id(summary_id: int) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM summaries WHERE id = ?", (summary_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_summary(summary_id: int) -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
        conn.commit()
        return cursor.rowcount > 0


def delete_summaries_bulk(ids: list) -> int:
    if not ids:
        return 0
    placeholders = ','.join('?' * len(ids))
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.execute(
            f"DELETE FROM summaries WHERE id IN ({placeholders})", ids
        )
        conn.commit()
        return cursor.rowcount


def demo_exists() -> bool:
    with sqlite3.connect(DATABASE_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM summaries WHERE source_name = 'יוסף לוי (דמו)' LIMIT 1"
        ).fetchone()
        return row is not None


def clean_demo_duplicates() -> None:
    """Delete all demo entries except the most recent one."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            DELETE FROM summaries
            WHERE source_name = 'יוסף לוי (דמו)'
            AND id NOT IN (
                SELECT id FROM summaries
                WHERE source_name = 'יוסף לוי (דמו)'
                ORDER BY created_at DESC
                LIMIT 1
            )
        """)
        conn.commit()


def update_demo_entry(summary: str, source_text: str) -> None:
    """Update the surviving demo entry to the latest summary and source text."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "UPDATE summaries SET summary = ?, source_text = ? WHERE source_name = 'יוסף לוי (דמו)'",
            (summary, source_text)
        )
        conn.commit()
