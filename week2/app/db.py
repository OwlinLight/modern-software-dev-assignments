from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


class InvalidNoteIdError(Exception):
    """note_id does not exist (foreign key constraint)."""


_NOTE_SELECT = "SELECT id, content, created_at FROM notes"
_ACTION_ITEM_SELECT = "SELECT id, note_id, text, done, created_at FROM action_items"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with Row factory and foreign keys enforced."""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if missing."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )
        conn.commit()


def insert_note(content: str) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        conn.commit()
        return int(cur.lastrowid)


def get_note(note_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"{_NOTE_SELECT} WHERE id = ?", (note_id,))
        return cur.fetchone()


def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    if not items:
        return []
    with get_connection() as conn:
        cur = conn.cursor()
        ids: list[int] = []
        try:
            for item in items:
                cur.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cur.lastrowid))
        except sqlite3.IntegrityError as exc:
            if "foreign key" in str(exc).lower():
                raise InvalidNoteIdError from exc
            raise
        conn.commit()
        return ids


def mark_action_item_done(action_item_id: int, done: bool) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        n = cur.rowcount
        conn.commit()
        return n


def list_action_items(note_id: int | None = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cur = conn.cursor()
        if note_id is None:
            cur.execute(f"{_ACTION_ITEM_SELECT} ORDER BY id DESC")
        else:
            cur.execute(
                f"{_ACTION_ITEM_SELECT} WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return list(cur.fetchall())
