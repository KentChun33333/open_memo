"""Mind map JSON loader with recursive node resolution."""

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel


class MindMapNode(BaseModel):
    """A single node in the mind map."""

    id: str
    label: str
    description: str = ""
    target_file: Optional[str] = None  # Path to another mind map or content
    children: list["MindMapNode"] = []
    style: dict[str, Any] = {}


class MindMapMeta(BaseModel):
    """Mind map metadata for listing."""

    id: str
    title: str
    description: str = ""
    node_count: int = 0


class MindMap(BaseModel):
    """A complete mind map."""

    id: str
    title: str
    description: str = ""
    nodes: list[MindMapNode] = []
    edges: list[dict[str, Any]] = []


class MindMapLoader:
    """Loads and resolves mind map JSON files."""

    def __init__(self, content_dir: Path):
        self.maps_dir = content_dir / "mind-maps"

    def list_maps(self) -> list[MindMapMeta]:
        """List all available mind maps."""
        maps = []
        if not self.maps_dir.exists():
            return maps

        for json_file in sorted(self.maps_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                node_count = self._count_nodes(data.get("nodes", []))
                maps.append(
                    MindMapMeta(
                        id=json_file.stem,
                        title=data.get("title", json_file.stem.replace("-", " ").title()),
                        description=data.get("description", ""),
                        node_count=node_count,
                    )
                )
            except (json.JSONDecodeError, Exception):
                continue

        return maps

    def get_map(self, map_id: str) -> Optional[MindMap]:
        """Load a specific mind map by ID."""
        json_file = self.maps_dir / f"{map_id}.json"
        if not json_file.exists():
            return None

        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            nodes = [self._parse_node(n) for n in data.get("nodes", [])]
            edges = data.get("edges", [])

            return MindMap(
                id=map_id,
                title=data.get("title", map_id.replace("-", " ").title()),
                description=data.get("description", ""),
                nodes=nodes,
                edges=edges,
            )
        except (json.JSONDecodeError, Exception):
            return None

    def get_node_content(self, map_id: str, target_file: str) -> Optional[dict[str, Any]]:
        """
        Resolve a node's targetFile reference.

        If targetFile points to another .json mind map, return its structure.
        If it points to a .md file, return the raw content.
        """
        base = self.maps_dir

        # Resolve relative path from mind-maps directory
        resolved = (base / target_file).resolve()

        # Security: ensure it's within content directory
        if not str(resolved).startswith(str(base.parent.resolve())):
            return None

        if not resolved.exists():
            return None

        if resolved.suffix == ".json":
            try:
                data = json.loads(resolved.read_text(encoding="utf-8"))
                return {"type": "mindmap", "data": data}
            except json.JSONDecodeError:
                return None
        elif resolved.suffix == ".md":
            content = resolved.read_text(encoding="utf-8")
            return {"type": "markdown", "content": content}
        else:
            return {"type": "text", "content": resolved.read_text(encoding="utf-8")}

    def _parse_node(self, data: dict) -> MindMapNode:
        """Parse a node dict into a MindMapNode."""
        children = [self._parse_node(c) for c in data.get("children", [])]
        return MindMapNode(
            id=data.get("id", ""),
            label=data.get("label", ""),
            description=data.get("description", ""),
            target_file=data.get("targetFile"),
            children=children,
            style=data.get("style", {}),
        )

    def _count_nodes(self, nodes: list) -> int:
        """Recursively count nodes."""
        count = len(nodes)
        for n in nodes:
            count += self._count_nodes(n.get("children", []))
        return count
