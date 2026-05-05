from __future__ import annotations

import json
import logging
import os
import re
from typing import List

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from ollama import Client, RequestError, ResponseError
from pydantic import BaseModel, ValidationError

load_dotenv()

logger = logging.getLogger(__name__)

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
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
    return first.lower() in imperative_starters

def extract_action_items_llm(text: str) -> List[str]:
    class ActionItems(BaseModel):
        action_items: List[str]

    schema = ActionItems.model_json_schema()
    timeout = float(os.getenv("OLLAMA_TIMEOUT", "120"))
    client = Client(timeout=timeout)
    try:
        response = client.chat(
            messages=[
                {
                    "role": "user",
                    "content": f"Extract action items from the following text: {text}",
                }
            ],
            model="llama3.1:8b",
            format=schema,
        )
    except (
        ConnectionError,
        RequestError,
        ResponseError,
        httpx.RequestError,
    ) as exc:
        logger.exception("Ollama request failed")
        raise HTTPException(
            status_code=503,
            detail="Model service unavailable",
        ) from exc

    raw = response.message.content
    try:
        return ActionItems.model_validate_json(raw).action_items
    except (ValidationError, json.JSONDecodeError, ValueError) as exc:
        logger.debug("Invalid LLM JSON response: %r", raw, exc_info=True)
        logger.warning("LLM response could not be parsed as structured action items")
        raise HTTPException(
            status_code=502,
            detail="Model returned an invalid response",
        ) from exc

