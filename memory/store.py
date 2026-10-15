"""SQLite storage for BLUE conversation history and explicit memories."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

MessageRole = Literal["user", "assistant", "system"]
_VALID_ROLES = {"user", "assistant", "system"}


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """One persisted message within a conversation session."""

    id: int
    session_id: str
    role: MessageRole
    content: str
    created_at: str


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """One explicitly saved long-term memory."""

    id: int
    content: str
    created_at: str
    updated_at: str


class MemoryStore:
    """Store conversation messages and user-approved memories in SQLite.

    Long-term memories are never created automatically by this class.
    Call add_memory() explicitly when a memory has been approved.
    """

    def __init__(self, db_path: str | Path) -> None:
        raw_path = str(db_path).strip()

        if not raw_path:
            raise ValueError("Database path must not be empty.")

        if raw_path == ":memory:":
            raise ValueError(
                "Provide a file-backed database path for persistent storage."
            )

        self._db_path = Path(raw_path).expanduser().resolve()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._db_path, timeout=5)
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL CHECK (length(trim(content)) > 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_messages_session_id
                    ON conversation_messages(session_id, id);

                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL CHECK (length(trim(content)) > 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_memories_updated_at
                    ON memories(updated_at, id);
                """
            )

    @staticmethod
    def _validate_text(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string.")

        if not value.strip():
            raise ValueError(f"{field} must not be empty.")

        return value.strip()

    @staticmethod
    def _validate_limit(limit: int, field: str = "limit") -> None:
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 1000
        ):
            raise ValueError(f"{field} must be an integer from 1 to 1000.")

    @staticmethod
    def _validate_id(record_id: int) -> None:
        if (
            not isinstance(record_id, int)
            or isinstance(record_id, bool)
        ):
            raise TypeError("Record ID must be an integer.")

        if record_id <= 0:
            raise ValueError("Record ID must be positive.")

    @staticmethod
    def _message_from_row(row: sqlite3.Row) -> ConversationMessage:
        return ConversationMessage(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _memory_from_row(row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
    ) -> ConversationMessage:
        """Persist one conversation message and return its stored record."""

        session_id = self._validate_text(session_id, "session_id")
        content = self._validate_text(content, "content")

        if not isinstance(role, str) or role not in _VALID_ROLES:
            raise ValueError(f"Unsupported conversation role: {role!r}")

        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO conversation_messages
                    (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                (session_id, role, content),
            )
            row = connection.execute(
                "SELECT * FROM conversation_messages WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

            if row is None:
                raise RuntimeError("Saved conversation message could not be read.")

            return self._message_from_row(row)

    def get_history(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[ConversationMessage]:
        """Return recent messages in chronological order."""

        session_id = self._validate_text(session_id, "session_id")
        self._validate_limit(limit)

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM conversation_messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        return [self._message_from_row(row) for row in reversed(rows)]

    def add_memory(self, content: str) -> MemoryRecord:
        """Save one explicitly approved long-term memory."""

        content = self._validate_text(content, "content")

        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO memories (content) VALUES (?)",
                (content,),
            )
            row = connection.execute(
                "SELECT * FROM memories WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

            if row is None:
                raise RuntimeError("Saved memory could not be read.")

            return self._memory_from_row(row)

    def list_memories(self, limit: int = 100) -> list[MemoryRecord]:
        """Return the most recently created memories first."""

        self._validate_limit(limit)

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM memories
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._memory_from_row(row) for row in rows]

    def search_memories(
        self,
        query: str,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        """Find memories containing a case-insensitive literal substring."""

        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        self._validate_limit(limit)
        query = query.strip()

        if not query:
            return []

        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM memories
                WHERE instr(lower(content), lower(?)) > 0
                ORDER BY id DESC
                LIMIT ?
                """,
                (query, limit),
            ).fetchall()

        return [self._memory_from_row(row) for row in rows]

    def update_memory(
        self,
        memory_id: int,
        content: str,
    ) -> MemoryRecord | None:
        """Update a saved memory, returning None when it does not exist."""

        self._validate_id(memory_id)
        content = self._validate_text(content, "content")

        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE memories
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (content, memory_id),
            )

            if cursor.rowcount == 0:
                return None

            row = connection.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,),
            ).fetchone()

            if row is None:
                return None

            return self._memory_from_row(row)

    def delete_memory(self, memory_id: int) -> bool:
        """Delete one memory; return whether a record was removed."""

        self._validate_id(memory_id)

        with self._connection() as connection:
            cursor = connection.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,),
            )
            return cursor.rowcount > 0
