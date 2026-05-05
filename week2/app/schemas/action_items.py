from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ActionItemExtractRequest(BaseModel):
    """POST /action-items/extract or /action-items/extract/llm — body."""

    text: str = Field(..., description="Source text to scan for tasks and action items.")
    save_note: bool = Field(
        False,
        description="If true, store `text` as a note and attach extracted items to it.",
    )

    @field_validator("text")
    @classmethod
    def strip_and_require_text(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("text is required")
        return s


class ExtractedActionItem(BaseModel):
    """One row returned right after extraction (includes new DB id)."""

    id: int = Field(..., description="Primary key of the stored action item.")
    text: str = Field(..., description="Normalized action item text.")


class ActionItemExtractResponse(BaseModel):
    """POST /action-items/extract — response."""

    note_id: int | None = Field(
        None,
        description="Set when `save_note` was true; otherwise null.",
    )
    items: list[ExtractedActionItem] = Field(
        default_factory=list,
        description="Persisted items in extraction order.",
    )


class ActionItemOut(BaseModel):
    """GET /action-items — each list element."""

    id: int
    note_id: int | None = Field(None, description="Owning note, if any.")
    text: str
    done: bool
    created_at: str = Field(..., description="SQLite `datetime('now')` string.")


class MarkActionItemDoneBody(BaseModel):
    """POST /action-items/{id}/done — body (optional fields use defaults)."""

    done: bool = Field(True, description="Whether the item is completed.")


class MarkActionItemDoneResponse(BaseModel):
    """POST /action-items/{id}/done — response."""

    id: int
    done: bool
