"""
Episodic Memory Store — "What happened"

Stores compressed episodes of past research sessions: what the agent did,
what it found, what the outcome was. Think of it as an experience diary.
"""

import json
import sqlite3
from datetime import datetime


class EpisodicStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episodic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    timestamp TEXT,
                    task_summary TEXT,
                    trajectory_summary TEXT,
                    outcome TEXT,
                    key_findings TEXT,
                    importance_score REAL,
                    embedding BLOB,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            conn.commit()

    def add(
        self,
        session_id: int,
        task_summary: str,
        trajectory_summary: str,
        outcome: str,
        key_findings: list[str],
        importance_score: float,
        embedding: list[float] | None = None,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO episodic
                    (session_id, timestamp, task_summary, trajectory_summary,
                     outcome, key_findings, importance_score, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    datetime.utcnow().isoformat(),
                    task_summary,
                    trajectory_summary,
                    outcome,
                    json.dumps(key_findings),
                    importance_score,
                    json.dumps(embedding) if embedding else None,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def search(self, top_k: int = 5) -> list[dict]:
        """Return top_k most recent episodes (retriever handles scoring)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM episodic
                ORDER BY session_id DESC
                LIMIT ?
                """,
                (top_k,),
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM episodic ORDER BY session_id ASC"
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_by_session(self, session_id: int) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM episodic WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            return self._row_to_dict(row) if row else None

    def increment_access(self, memory_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE episodic
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE id = ?
                """,
                (datetime.utcnow().isoformat(), memory_id),
            )
            conn.commit()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM episodic").fetchone()[0]
            return {"count": count, "type": "episodic"}

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        d["key_findings"] = json.loads(d["key_findings"]) if d["key_findings"] else []
        d["embedding"] = json.loads(d["embedding"]) if d["embedding"] else None
        d["memory_type"] = "episodic"
        # Build content string for retrieval/display
        d["content"] = (
            f"Session {d['session_id']}: {d['task_summary']}\n"
            f"Outcome: {d['outcome']}\n"
            f"Key findings: {', '.join(d['key_findings'])}"
        )
        return d
