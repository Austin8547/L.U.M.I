
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4



PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "lumi_memory.db"


class ConversationMemory:
    """SQLite-based persistent conversation memory for Lumi."""

    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self):
        """Create a database connection."""
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        """Create the messages table if it does not exist."""
        with self._connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages (session_id, id)
            """)

    @staticmethod
    def create_session():
        """Create a unique ID for a new conversation."""
        return str(uuid4())

    def save_message(self, session_id, role, content):
        """Save one user or assistant message."""
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")

        if role not in {"user", "assistant"}:
            raise ValueError("role must be 'user' or 'assistant'")

        if not isinstance(content, str) or not content.strip():
            raise ValueError("content cannot be empty")

        timestamp = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages
                    (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content.strip(), timestamp),
            )

    def get_history(self, session_id, limit=20):
        """
        Return the most recent messages in chronological order.

        The returned format can be passed to Lumi's message-based agents.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content
                FROM (
                    SELECT id, role, content
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
                """,
                (session_id, limit),
            ).fetchall()

        return [
            {"role": row["role"], "content": row["content"]}
            for row in rows
        ]

    def clear_session(self, session_id):
        """Delete messages belonging to one conversation."""
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,),
            )
