from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas.notes import NoteCreateRequest, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get(
    "",
    response_model=list[NoteOut],
    summary="List all notes",
)
def get_all_notes() -> list[NoteOut]:
    rows = db.list_notes()
    return [
        NoteOut(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.post(
    "",
    response_model=NoteOut,
    summary="Create a note",
)
def create_note(payload: NoteCreateRequest) -> NoteOut:
    content = payload.content
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="failed to load created note")
    return NoteOut(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note by id",
)
def get_single_note(note_id: int) -> NoteOut:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut(
        id=row["id"],
        content=row["content"],
        created_at=row["created_at"],
    )
