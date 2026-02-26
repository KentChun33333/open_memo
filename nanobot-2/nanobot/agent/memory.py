"""Advanced Memory system using LanceDB hybrid search."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import lancedb
    from lancedb.pydantic import LanceModel, Vector
    from lancedb.embeddings import get_registry
    
    # Try to use local Ollama initially, fallback to sentence-transformers if needed
    try:
        embed_func = get_registry().get("ollama").create(name="embeddinggemma", max_retries=1)
    except Exception:
        embed_func = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2")

    class MemoryItem(LanceModel):
        id: str
        vector: Vector(embed_func.ndims()) = embed_func.VectorField() # type: ignore
        text: str
        memory_type: str  # "long_term", "conversation", "observation"
        scope: str
        timestamp: datetime
        is_valid: bool = True

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False


from nanobot.utils.helpers import ensure_dir


class MemoryStore:
    """Advanced Memory Store using LanceDB for BM25 and Vector Hybrid Search."""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory_dir = ensure_dir(workspace / "memory")
        
        # Legacy fallback for smooth transition
        self.legacy_memory_file = self.memory_dir / "MEMORY.md"
        self.legacy_history_file = self.memory_dir / "HISTORY.md"
        
        self.table = None
        if LANCEDB_AVAILABLE:
            try:
                self.db = lancedb.connect(str(self.memory_dir / "memory.lance"))
                table_name = "agent_memory"
                if table_name not in self.db.table_names():
                    self.table = self.db.create_table(table_name, schema=MemoryItem)
                    # Create FTS index for BM25 (requires tantivy)
                    try:
                        self.table.create_fts_index("text")
                    except Exception:
                        pass
                else:
                    self.table = self.db.open_table(table_name)
            except Exception as e:
                print(f"Warning: Failed to initialize LanceDB: {e}")
                self.table = None

    def read_long_term(self) -> str:
        if self.legacy_memory_file.exists():
            return self.legacy_memory_file.read_text(encoding="utf-8")
        return ""

    def add_memory(self, text: str, memory_type: str, scope: str = "global") -> None:
        """Add a new memory item to LanceDB."""
        if not text.strip() or not self.table:
            return
            
        item = {
            "id": str(uuid.uuid4()),
            "text": text,
            "memory_type": memory_type,
            "scope": scope,
            "timestamp": datetime.now(),
            "is_valid": True
        }
        try:
            self.table.add([item])
            # Update FTS index if Tantivy is available
            try:
                self.table.create_fts_index("text", replace=True)
            except Exception:
                pass
        except Exception as e:
            print(f"Failed to add to LanceDB: {e}")

    def write_long_term(self, content: str) -> None:
        """Legacy compatibility - writes to LanceDB as long_term memory."""
        self.add_memory(content, memory_type="long_term")
        # Keep legacy file updated just in case
        if content.strip():
            self.legacy_memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str) -> None:
        """Legacy compatibility - writes to LanceDB as conversation history."""
        self.add_memory(entry, memory_type="conversation")
        # Keep legacy file updated
        with open(self.legacy_history_file, "a", encoding="utf-8") as f:
            f.write(entry.rstrip() + "\n\n")

    def search_memory(self, query: str, limit: int = 3) -> list[dict]:
        """Perform Hybrid Search (Vector + BM25) on LanceDB."""
        if not self.table:
            return []
            
        if not query:
            try:
                df = self.table.to_pandas()
                if not df.empty:
                    df = df[df["is_valid"] == True]
                    df = df.sort_values(by="timestamp", ascending=False).head(limit)
                    return df.to_dict(orient="records")
            except Exception:
                pass
            return []
            
        try:
            # Attempt Hybrid Search (requires tantivy to be properly indexed)
            res = self.table.search(query, query_type="hybrid").where("is_valid = true").limit(limit).to_pandas()
            return res.to_dict(orient="records")
        except Exception:
            try:
                # Fallback to vector-only search if FTS fails
                res = self.table.search(query).where("is_valid = true").limit(limit).to_pandas()
                return res.to_dict(orient="records")
            except Exception:
                return []

    def delete_memory(self, memory_id: Optional[str] = None, memory_type: Optional[str] = None) -> int:
        """
        Soft-delete memories by their ID or type to resolve context contamination without removing the negative constraint.
        Returns the number of rows invalidated.
        """
        if not self.table:
            return 0
            
        try:
            if memory_id:
                # LanceDB soft deletion using update
                self.table.update(where=f"id = '{memory_id}'", values={"is_valid": False})
                return 1
            elif memory_type:
                self.table.update(where=f"memory_type = '{memory_type}'", values={"is_valid": False})
                return 1
        except Exception as e:
            print(f"Failed to delete from LanceDB: {e}")
            
        return 0

    def get_memory_context(self, query: Optional[str] = None) -> str:
        """Retrieve the most relevant context for the current query/state."""
        # 1. Always include Long Term core facts (legacy or active)
        long_term = self.read_long_term()
        parts = []
        if long_term:
            parts.append(f"## Core Long-term Memory\n{long_term}")
            
        # 2. Get dynamic Implicit RAG context from LanceDB based on user query
        if query and self.table:
            results = self.search_memory(query, limit=3)
            if results:
                mem_texts = []
                for r in results:
                    # Format timestamp cleanly
                    ts = r['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(r['timestamp'], datetime) else r['timestamp']
                    mem_texts.append(f"- [{ts}] ({r['memory_type']}): {r['text']}")
                parts.append("## Relevant Retrieved Memories\n" + "\n".join(mem_texts))
                
        return "\n\n".join(parts) if parts else ""
