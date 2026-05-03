import random

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def _assert_list_equal_ignore_case(actual: list[str], expected: list[str]) -> None:
    assert [x.casefold() for x in actual] == [x.casefold() for x in expected]


def _assert_any_matches_ignore_case(items: list[str], needle: str) -> None:
    n = needle.casefold()
    assert any(x.casefold() == n for x in items), (
        f"expected an item matching {needle!r} (ignore case), got {items!r}"
    )


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_bullets_and_checkboxes_llm():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items_llm(text)
    _assert_any_matches_ignore_case(items, "Set up database")
    _assert_any_matches_ignore_case(items, "implement API extract endpoint")
    _assert_any_matches_ignore_case(items, "Write tests")


# Todo: Write unit tests for extract_action_items_llm() covering multiple inputs
# (e.g., bullet lists, keyword-prefixed lines, empty input)


def test_extract_action_items_llm():
    # Test case 1: Empty input
    text = ""
    items = extract_action_items_llm(text)
    assert items == []

    # Test case 2: Input with only narrative sentence
    text = "Some narrative sentence."
    items = extract_action_items_llm(text)
    assert items == []

    # Test case 3: Input with only keyword-prefixed lines
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    starter = random.choice(list(imperative_starters))
    text = (
        f"I will try my best to {starter} a list of reports to review, "
        "regardless of the outcome."
    )
    items = extract_action_items_llm(text)
    _assert_list_equal_ignore_case(
        items, [f"{starter} a list of reports to review"]
    )

    # Test case 4: Input with only bullet list
    text = "- [ ] Set up database"
    items = extract_action_items_llm(text)
    _assert_list_equal_ignore_case(items, ["Set up database"])
