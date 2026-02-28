"""
Reflective Memory Store — "What I learned"

Stores meta-cognitive lessons derived from experience.
Example: "Leadership changes correlate with financial risk signals"

These are higher-order insights that guide future behavior.
"""

import json
import sqlite3
from datetime import datetime


class ReflectiveStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reflective (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson TEXT,
                    context TEXT,
                    derived_from TEXT,
                    importance_score REAL,
                    embedding BLOB,
                    access_count INTEGER DEFAULT 0,
                    created_at TEXT
                )
            """)
            conn.commit()

    def add(
        self,
        lesson: str,
        context: str,
        derived_from: list[int] | None = None,
        importance_score: float = 0.7,
        embedding: list[float] | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO reflective
                    (lesson, context, derived_from, importance_score,
                     embedding, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lesson,
                    context,
                    json.dumps(derived_from) if derived_from else "[]",
                    importance_score,
                    json.dumps(embedding) if embedding else None,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def search(self, top_k: int = 10) -> list[dict]:
        """Return top lessons by importance (retriever handles full scoring)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM reflective
                ORDER BY importance_score DESC
                LIMIT ?
                """,
                (top_k,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM reflective ORDER BY importance_score DESC"
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def increment_access(self, memory_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE reflective SET access_count = access_count + 1 WHERE id = ?",
                (memory_id,),
            )
            conn.commit()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM reflective").fetchone()[0]
            avg_importance = conn.execute(
                "SELECT COALESCE(AVG(importance_score), 0) FROM reflective"
            ).fetchone()[0]
            return {
                "count": count,
                "avg_importance": round(avg_importance, 2),
                "type": "reflective",
            }

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        d["derived_from"] = (
            json.loads(d["derived_from"]) if d["derived_from"] else []
        )
        d["embedding"] = json.loads(d["embedding"]) if d["embedding"] else None
        d["memory_type"] = "reflective"
        d["content"] = f"Lesson: {d['lesson']}\nContext: {d['context']}"
        return d
