from itertools import accumulate
import os
import random
import pytest
from ..app.services.extract import extract_action_items, extract_action_items_llm

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
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items

#Todo: Write unit tests for extract_action_items_llm() covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) 

def test_extract_action_items_llm():
    #Test case 1: Empty input
    text = ""
    items = extract_action_items_llm(text)
    assert items == []

    #Test case 2: Input with only narrative sentence
    text = "Some narrative sentence."
    items = extract_action_items_llm(text)
    assert items == []

    #Test case 3: Input with only keyword-prefixed lines
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
    # starter is a random item from the imperative_starters set
    starter = random.choice(list(imperative_starters))
    text = f"I will try my best to {starter} a list of reports to review, regardless of the outcome."
    items = extract_action_items_llm(text)


    assert items == [f"{starter} a list of reports to review"]

    #Test case 4: Input with only bullet list
    text = "- [ ] Set up database"
    items = extract_action_items_llm(text)
    assert items == ["Set up database"]

if __name__ == "__main__":
    pytest.main()