from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class NoteCreateRequest(BaseModel):
    """POST /notes — body."""

    content: str = Field(..., description="Note body text.")

    @field_validator("content")
    @classmethod
    def strip_and_require_content(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("content is required")
        return s


class NoteOut(BaseModel):
    """GET /notes/{id} and POST /notes — response shape."""

    id: int
    content: str
    created_at: str = Field(..., description="SQLite `datetime('now')` string.")
