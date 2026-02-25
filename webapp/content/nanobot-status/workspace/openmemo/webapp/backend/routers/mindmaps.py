"""Mind map API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException

from backend.config import settings
from backend.services.mindmap_loader import MindMap, MindMapLoader, MindMapMeta

router = APIRouter(prefix="/api/mindmaps", tags=["mindmaps"])

loader = MindMapLoader(settings.content_dir)


@router.get("", response_model=list[MindMapMeta])
async def list_mindmaps():
    """List all available mind maps."""
    return loader.list_maps()


@router.get("/{map_id}", response_model=MindMap)
async def get_mindmap(map_id: str):
    """Get a specific mind map by ID."""
    mindmap = loader.get_map(map_id)
    if not mindmap:
        raise HTTPException(status_code=404, detail=f"Mind map '{map_id}' not found")
    return mindmap


@router.get("/{map_id}/resolve")
async def resolve_target(map_id: str, target: str) -> dict[str, Any]:
    """
    Resolve a node's targetFile reference.

    Returns either a linked mind map or markdown content.
    """
    result = loader.get_node_content(map_id, target)
    if not result:
        raise HTTPException(status_code=404, detail=f"Target '{target}' not found")
    return result
