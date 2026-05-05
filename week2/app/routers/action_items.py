from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException, Query

from .. import db
from ..schemas.action_items import (
    ActionItemExtractRequest,
    ActionItemExtractResponse,
    ActionItemOut,
    ExtractedActionItem,
    MarkActionItemDoneBody,
    MarkActionItemDoneResponse,
)
from ..services.extract import extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post(
    "/extract",
    response_model=ActionItemExtractResponse,
    summary="Extract and persist action items from text",
)
def extract(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    text = payload.text
    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemExtractResponse(
        note_id=note_id,
        items=[
            ExtractedActionItem(id=i, text=t) for i, t in zip(ids, items, strict=True)
        ],
    )


@router.get(
    "",
    response_model=list[ActionItemOut],
    summary="List action items",
)
def list_all(
    note_id: int | None = Query(
        None,
        description="Filter by owning note id; omit to return all items.",
    ),
) -> list[ActionItemOut]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemOut(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post(
    "/{action_item_id}/done",
    response_model=MarkActionItemDoneResponse,
    summary="Set completion flag on an action item",
)
def mark_done(
    action_item_id: int,
    body: MarkActionItemDoneBody = Body(),
) -> MarkActionItemDoneResponse:
    db.mark_action_item_done(action_item_id, body.done)
    return MarkActionItemDoneResponse(id=action_item_id, done=body.done)
