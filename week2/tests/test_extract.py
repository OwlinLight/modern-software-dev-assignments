import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from ..app.services.extract import extract_action_items, extract_action_items_llm

# TODO 1: Add an optional `@pytest.mark.integration` test that calls live Ollama when
# OLLAMA_HOST is set (skip otherwise), to complement these mocked unit tests.

MEETING_NOTES = """
Notes from meeting:
- [ ] Set up database
* implement API extract endpoint
1. Write tests
Some narrative sentence.
""".strip()


def test_extract_bullets_and_checkboxes():
    items = extract_action_items(MEETING_NOTES)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


@pytest.fixture
def mock_llm_chat():
    with patch("week2.app.services.extract.chat") as mock_chat:
        yield mock_chat


@pytest.mark.parametrize(
    "input_text, action_items_from_model",
    [
        (
            MEETING_NOTES,
            ["Set up database", "implement API extract endpoint", "Write tests"],
        ),
        ("", []),
    ],
)
def test_extract_action_items_llm(mock_llm_chat, input_text, action_items_from_model):
    mock_llm_chat.return_value = SimpleNamespace(
        message=SimpleNamespace(
            content=json.dumps({"action_items": action_items_from_model})
        )
    )
    assert extract_action_items_llm(input_text) == action_items_from_model


def test_extract_action_items_llm_invalid_json_raises(mock_llm_chat):
    mock_llm_chat.return_value = SimpleNamespace(
        message=SimpleNamespace(content="not valid json")
    )
    with pytest.raises(ValidationError):
        extract_action_items_llm("any")
