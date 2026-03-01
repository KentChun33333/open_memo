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
        
        # Schema evolution backfill state
        self.watermarks_file = self.memory_dir / "backfill_watermarks.json"
        self._load_watermarks()
        
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

    def add_memory(self, text: str, memory_type: str, scope: str = "global", metadata: dict | None = None) -> None:
        """Add a new memory item to LanceDB with dynamic metadata columns."""
        if not text.strip() or self.table is None:
            return
            
        item = {
            "id": str(uuid.uuid4()),
            "text": text,
            "memory_type": memory_type,
            "scope": scope,
            "timestamp": datetime.now(),
            "is_valid": True
        }
        
        if metadata:
            for k, v in metadata.items():
                item[k] = str(v)

        try:
            # Get the exact current schema of the LanceDB table
            current_schema = self.table.schema
            current_columns = current_schema.names
            
            new_columns = {}
            for k in item.keys():
                if k not in current_columns:
                    new_columns[k] = "''"  # default empty string syntax
            
            if new_columns:
                self.table.add_columns(new_columns)
                current_schema = self.table.schema
                current_columns = current_schema.names

            # Fill in any existing schema columns that are missing from the current item
            # LanceDB requires that the dict exactly matches the explicit Schema fields
            for col in current_columns:
                if col not in item and col != "vector":
                    # Determine the pyarrow type for the missing column to provide the right default
                    field = current_schema.field(col)
                    if "timestamp" in str(field.type).lower():
                        item[col] = datetime.now()
                    elif "bool" in str(field.type).lower():
                        item[col] = False
                    else:
                        item[col] = ""

            self.table.add([item])
            
            # Real tqdm progress bar
            try:
                from tqdm import tqdm
                if getattr(self, '_pbar', None) is None:
                    self._pbar = tqdm(desc="[LanceDB] 🧠 Indexing memory", unit=" rec")
                self._pbar.update(1)
            except ImportError:
                # Fallback to in-place print if tqdm isn't installed
                count = len(self.table)
                print(f"\r[LanceDB] 🧠 Indexing memory... ⏳ Total saved: {count} records", end="", flush=True)
            # Update FTS index if Tantivy is available
            try:
                self.table.create_fts_index("text", replace=True)
            except Exception:
                pass
        except Exception as e:
            print(f"Failed to add to LanceDB: {e}")
            import traceback
            traceback.print_exc()

    def write_long_term(self, content: str, metadata: dict | None = None) -> None:
        """Legacy compatibility - writes to LanceDB as long_term memory."""
        self.add_memory(content, memory_type="long_term", metadata=metadata)
        # Keep legacy file updated just in case
        if content.strip():
            self.legacy_memory_file.write_text(content, encoding="utf-8")

    def append_history(self, entry: str, metadata: dict | None = None) -> None:
        """Legacy compatibility - writes to LanceDB as conversation history."""
        self.add_memory(entry, memory_type="conversation", metadata=metadata)
        # Keep legacy file updated
        with open(self.legacy_history_file, "a", encoding="utf-8") as f:
            f.write(entry.rstrip() + "\n\n")

    def search_memory(self, query: str, limit: int = 3, filters: dict | None = None) -> list[dict]:
        """Perform Hybrid Search (Vector + BM25) on LanceDB with D-RAG Subspace Filtering."""
        if self.table is None:
            return []
            
        where_clauses = ["is_valid = true"]
        if filters:
            for k, v in filters.items():
                if k in self.table.schema.names:
                    # Short-term fallback: allow strict matches OR empty strings OR nulls
                    # This guarantees we don't drop old documents when a schema evolves under them
                    where_clauses.append(f"({k} = '{v}' OR {k} = '')")
        
        where_stmt = " AND ".join(where_clauses)
            
        if not query:
            try:
                df = self.table.to_pandas()
                if not df.empty:
                    df = df[df["is_valid"] == True]
                    if filters:
                        for k, v in filters.items():
                            if k in df.columns:
                                df = df[df[k] == str(v)]
                    df = df.sort_values(by="timestamp", ascending=False).head(limit)
                    return df.to_dict(orient="records")
            except Exception:
                pass
            return []
            
        try:
            # Attempt Hybrid Search (requires tantivy to be properly indexed)
            res = self.table.search(query, query_type="hybrid").where(where_stmt).limit(limit).to_pandas()
            return res.to_dict(orient="records")
        except Exception:
            try:
                # Fallback to vector-only search if FTS fails
                res = self.table.search(query).where(where_stmt).limit(limit).to_pandas()
                return res.to_dict(orient="records")
            except Exception:
                return []

    def delete_memory(self, memory_id: Optional[str] = None, memory_type: Optional[str] = None) -> int:
        """
        Soft-delete memories by their ID or type to resolve context contamination without removing the negative constraint.
        Returns the number of rows invalidated.
        """
        if self.table is None:
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

    def get_memory_context(self, query: Optional[str] = None, filters: Optional[dict] = None) -> str:
        """Retrieve the most relevant context for the current query/state."""
        # 1. Always include Long Term core facts (legacy or active)
        long_term = self.read_long_term()
        parts = []
        if long_term:
            parts.append(f"## Core Long-term Memory\n{long_term}")
            
        # 2. Get dynamic Implicit RAG context from LanceDB based on user query
        if query and self.table:
            results = self.search_memory(query, limit=3, filters=filters)
            if results:
                mem_texts = []
                for r in results:
                    # Format timestamp cleanly
                    ts = r['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(r['timestamp'], datetime) else r['timestamp']
                    mem_texts.append(f"- [{ts}] ({r['memory_type']}): {r['text']}")
                parts.append("## Relevant Retrieved Memories\n" + "\n".join(mem_texts))
                
        return "\n\n".join(parts) if parts else ""

    def _load_watermarks(self) -> None:
        import json
        if self.watermarks_file.exists():
            try:
                self.watermarks = json.loads(self.watermarks_file.read_text(encoding="utf-8"))
            except Exception:
                self.watermarks = {}
        else:
            self.watermarks = {}

    def save_watermark(self, dimension: str, timestamp_val: float) -> None:
        import json
        self.watermarks[dimension] = timestamp_val
        self.watermarks_file.write_text(json.dumps(self.watermarks), encoding="utf-8")

    def get_records_for_backfill(self, dimension: str, promotion_ts: float, watermark_ts: float, limit: int = 50) -> list[dict]:
        """Fetch up to `limit` raw untagged records bounding the watermark period."""
        if self.table is None or dimension not in self.table.schema.names:
            return []
            
        try:
            import pandas as pd
            from datetime import datetime
            # Pull via pandas for explicit timestamp comparison logic
            df = self.table.search().limit(10000).to_pandas()
            if df.empty:
                return []
                
            df_ts = pd.to_datetime(df['timestamp'])
            
            # addition of 0.001 to handle precision truncation
            promotion_dt = pd.to_datetime(datetime.fromtimestamp(promotion_ts + 0.001))
            watermark_dt = pd.to_datetime(datetime.fromtimestamp(watermark_ts)) if watermark_ts > 1000 else pd.Timestamp.min
            
            # Timestamp window filter bounds
            mask = (df_ts > watermark_dt) & (df_ts <= promotion_dt) & (df['is_valid'] == True)
            
            # Ensure it is currently empty string
            if dimension in df.columns:
                mask = mask & ((df[dimension] == '') | df[dimension].isnull())
            else:
                return []
                
            filtered = df[mask].sort_values(by="timestamp", ascending=True).head(limit)
            return filtered.to_dict(orient="records")
        except Exception as e:
            print(f"Error fetching backfill records: {e}")
            return []

    def update_memory_metadata(self, memory_id: str, updates: dict) -> bool:
        """Dynamically update metadata schema values on a specific vector memory."""
        if self.table is None:
            return False
        try:
            self.table.update(where=f"id = '{memory_id}'", values=updates)
            return True
        except Exception as e:
            print(f"Failed memory backfill update: {e}")
            return False
