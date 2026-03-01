"""Memory interaction tools for reading and writing to LanceDB."""

import os
from pathlib import Path
from typing import Any

from loguru import logger

from nanobot.agent.tools.base import Tool
from nanobot.agent.memory import MemoryStore


class SearchMemoryTool(Tool):
    """Tool to search historical conversational context and facts from the agent's LanceDB database."""
    
    @property
    def name(self) -> str:
        return "search_memory"
    
    @property
    def description(self) -> str:
        return "Search the agent's long-term and short-term conversational historical memory in LanceDB. Returns a list of documents with metadata. Use when you need to remember past interactions or facts."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or keyword to look for in past conversations. Example: 'Polymarket' or 'Docker deployment setup'"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of historical records to return (default 10). Keep this small to avoid cluttering your context.",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        
    async def execute(self, query: str, limit: int = 10, **kwargs: Any) -> str:
        if not self.workspace:
            return "Error: Workspace path could not be resolved."
            
        try:
            store = MemoryStore(self.workspace)
            results = store.search_memory(query, limit=limit)
            
            if not results:
                return f"No memories found matching: '{query}'"
                
            formatted = [f"Found {len(results)} records matching '{query}':"]
            for r in results:
                score = f" (score: {r['score']:.2f})" if r.get('score') else ""
                meta = " | ".join(f"{k}: {v}" for k, v in r.get("metadata", {}).items() if v)
                meta_str = f" [{meta}]" if meta else ""
                type_indicator = f"[{r['memory_type'].upper()}] " if 'memory_type' in r else ""
                
                formatted.append(f"- {type_indicator}{r.get('timestamp', 'Unknown Time')}{score}{meta_str}:\n    {r['text']}")
            
            return "\n\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return f"Error executing memory search: {str(e)}"


class WriteMemoryTool(Tool):
    """Tool to force a permanent fact into the highest-priority long-term LanceDB collection."""
    
    @property
    def name(self) -> str:
        return "write_memory"
    
    @property
    def description(self) -> str:
        return "Commit an important, permanent, structural fact to the core Long Term Memory space (e.g., API keys, deployment paths, user preferences). This completely overwrites the global facts section, so ensure you merge existing facts if necessary."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The full markdown content of all long term facts to be saved safely into LanceDB and legacy fallback."
                }
            },
            "required": ["content"]
        }
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        
    async def execute(self, content: str, **kwargs: Any) -> str:
        if not self.workspace:
            return "Error: Workspace path could not be resolved."
            
        try:
            store = MemoryStore(self.workspace)
            store.write_long_term(content)
            return "Successfully updated core Long Term Memory facts."
        except Exception as e:
            logger.error(f"Failed to write long term memory: {e}")
            return f"Error writing to memory store: {str(e)}"


class DeleteMemoryTool(Tool):
    """Tool to remove hallucinated or bad vectors out of the active LanceDB memory scope."""
    
    @property
    def name(self) -> str:
        return "delete_memory"
    
    @property
    def description(self) -> str:
        return "Delete specific contaminated or hallucinated memory rows from the database using their unique memory_id."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The exact string UUID of the memory entry to permanently delete (found via search_memory tool)."
                }
            },
            "required": ["memory_id"]
        }
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        
    async def execute(self, memory_id: str, **kwargs: Any) -> str:
        if not self.workspace:
            return "Error: Workspace path could not be resolved."
            
        try:
            store = MemoryStore(self.workspace)
            rows = store.delete_memory(memory_id)
            return f"Operation complete. Removed {rows} occurrences of memory id '{memory_id}'."
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return f"Error deleting memory vector: {str(e)}"
