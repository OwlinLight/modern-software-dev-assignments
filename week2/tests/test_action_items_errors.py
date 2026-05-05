"""HTTP behavior for LLM extract, mark-done, and FK integrity."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ..app import db
from ..app.db import InvalidNoteIdError
from ..app.main import app
from ..app.services import extract as extract_svc


client = TestClient(app)

LLM_EXTRACT = "/action-items/extract/llm"


def test_insert_action_items_invalid_note_id_raises() -> None:
    db.init_db()
    with pytest.raises(InvalidNoteIdError):
        db.insert_action_items(["orphan"], note_id=999_999_999)


def test_mark_done_missing_returns_404() -> None:
    r = client.post("/action-items/999999999/done", json={"done": True})
    assert r.status_code == 404
    assert r.json()["detail"] == "action item not found"


@patch.object(extract_svc, "Client")
def test_extract_ollama_unavailable_returns_503(mock_client_cls: MagicMock) -> None:
    mock_client_cls.return_value.chat.side_effect = ConnectionError("refused")
    r = client.post(
        LLM_EXTRACT, json={"text": "buy milk", "save_note": False}
    )
    assert r.status_code == 503
    assert r.json()["detail"] == "Model service unavailable"


@patch.object(extract_svc, "Client")
def test_extract_invalid_llm_json_returns_502(mock_client_cls: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.message.content = "not valid json"
    mock_client_cls.return_value.chat.return_value = mock_response
    r = client.post(
        LLM_EXTRACT, json={"text": "buy milk", "save_note": False}
    )
    assert r.status_code == 502
    assert r.json()["detail"] == "Model returned an invalid response"


@patch("week2.app.routers.action_items.extract_action_items_llm", return_value=["x"])
@patch("week2.app.routers.action_items.db.insert_action_items")
def test_extract_invalid_note_id_returns_400(
    mock_insert: MagicMock,
    _mock_llm: MagicMock,
) -> None:
    mock_insert.side_effect = InvalidNoteIdError()
    r = client.post(
        LLM_EXTRACT, json={"text": "buy milk", "save_note": False}
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "invalid note_id"
