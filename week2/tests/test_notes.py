"""HTTP behavior for note collection and single-note endpoints."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ..app import db
from ..app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(db, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    db.init_db()


def test_list_notes_returns_all_notes_newest_first() -> None:
    first_id = db.insert_note("first note")
    second_id = db.insert_note("second note")

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json()[:2] == [
        {
            "id": second_id,
            "content": "second note",
            "created_at": response.json()[0]["created_at"],
        },
        {
            "id": first_id,
            "content": "first note",
            "created_at": response.json()[1]["created_at"],
        },
    ]


def test_get_single_note_missing_returns_404() -> None:
    response = client.get("/notes/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "note not found"
