from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .db import get_db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


@dataclass
class User:
    id: int
    google_sub: str
    email: str
    name: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            google_sub=row["google_sub"],
            email=row["email"],
            name=row["name"],
        )


@dataclass
class Entry:
    id: int
    user_id: int
    title: str
    content: str
    written_at: str
    unlock_at: str
    opened_at: str | None

    @property
    def written_at_dt(self) -> datetime:
        return parse_iso_datetime(self.written_at)

    @property
    def unlock_at_dt(self) -> datetime:
        return parse_iso_datetime(self.unlock_at)

    @property
    def is_unlocked(self) -> bool:
        return utc_now() >= self.unlock_at_dt

    @property
    def is_new(self) -> bool:
        return self.is_unlocked and self.opened_at is None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            content=row["content"],
            written_at=row["written_at"],
            unlock_at=row["unlock_at"],
            opened_at=row["opened_at"],
        )


def get_user_by_id(user_id: int) -> User | None:
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return User.from_row(row) if row else None


def get_user_by_google_sub(google_sub: str) -> User | None:
    row = get_db().execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
    return User.from_row(row) if row else None


def create_or_update_user(google_sub: str, email: str, name: str) -> User:
    db = get_db()
    existing = get_user_by_google_sub(google_sub)
    if existing:
        db.execute(
            """
            UPDATE users
            SET email = ?, name = ?
            WHERE id = ?
            """,
            (email, name, existing.id),
        )
        db.commit()
        return get_user_by_id(existing.id)

    cursor = db.execute(
        """
        INSERT INTO users (google_sub, email, name)
        VALUES (?, ?, ?)
        """,
        (google_sub, email, name),
    )
    db.commit()
    return get_user_by_id(cursor.lastrowid)


def create_entry(user_id: int, title: str, content: str, written_at: str, unlock_at: str) -> None:
    db = get_db()
    db.execute(
        """
        INSERT INTO entries (user_id, title, content, written_at, unlock_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, title, content, written_at, unlock_at),
    )
    db.commit()


def get_entries_for_user(user_id: int) -> list[Entry]:
    rows = get_db().execute(
        """
        SELECT * FROM entries
        WHERE user_id = ?
        ORDER BY unlock_at ASC, created_at DESC
        """,
        (user_id,),
    ).fetchall()
    return [Entry.from_row(row) for row in rows]


def get_entry_for_user(user_id: int, entry_id: int) -> Entry | None:
    row = get_db().execute(
        """
        SELECT * FROM entries
        WHERE id = ? AND user_id = ?
        """,
        (entry_id, user_id),
    ).fetchone()
    return Entry.from_row(row) if row else None


def mark_entry_opened(entry_id: int) -> None:
    db = get_db()
    db.execute(
        """
        UPDATE entries
        SET opened_at = COALESCE(opened_at, ?)
        WHERE id = ?
        """,
        (utc_now().isoformat(), entry_id),
    )
    db.commit()
