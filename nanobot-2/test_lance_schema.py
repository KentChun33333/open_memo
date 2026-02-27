import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
import shutil
import pandas as pd
import pyarrow as pa

# Try to use local Ollama initially, fallback to sentence-transformers if needed
try:
    embed_func = get_registry().get("ollama").create(name="embeddinggemma", max_retries=1)
except Exception:
    embed_func = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2")

class MemoryItem(LanceModel):
    id: str
    vector: Vector(embed_func.ndims()) = embed_func.VectorField() # type: ignore
    text: str
    is_valid: bool = True

db_path = "./test_lance_lancedb"
shutil.rmtree(db_path, ignore_errors=True)

db = lancedb.connect(db_path)
table = db.create_table("memories", schema=MemoryItem)

item1 = {
    "id": "1",
    "text": "Hello world",
    "is_valid": True
}
table.add([item1])
print("Added item 1")

# Now try to add a new column dynamically via pandas
data = {
    "id": ["2"],
    "text": ["Hello again"],
    "is_valid": [True],
    "project": ["Alpha"]
}
df = pd.DataFrame(data)

try:
    # LanceDB might not like schema change on add
    table.add(df, mode="append")
    print("Added item 2 with new column!")
except Exception as e:
    print("Error adding item 2:", e)

# Try merging schema
try:
    table.add(df, schema=pa.Schema.from_pandas(df))
    print("Added with explicit schema merge!")
except Exception as e:
    print("Error with explicit schema merge:", e)

print("Columns:", table.schema.names)
