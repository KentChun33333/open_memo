"""Notes API endpoints."""

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.services.content_loader import ContentItem, ContentLoader

router = APIRouter(prefix="/api/notes", tags=["notes"])

loader = ContentLoader(settings.content_dir, sub_dir="notes")


class NoteListItem(ContentItem):
    """Note item without full HTML for list views."""

    html: str = ""
    raw: str = ""


@router.get("", response_model=list[NoteListItem])
async def list_notes():
    """List all notes (without full content)."""
    return loader.list_items()


@router.get("/{slug}", response_model=ContentItem)
async def get_note(slug: str):
    """Get a single note by slug."""
    note = loader.get_item(slug)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note '{slug}' not found")
    return note
