---
name: "memory"
description: "Explicitly query the LanceDB agent memory for historical depth, or memorize critical long-term facts."
---

# memory

This skill allows you to manually interact with the `memory.lance` hybrid database for cases where the implicit short-term context injected into your system prompt is not enough.

You should use this skill when:

- You need to search far back into conversation history (>3 turns).
- You want to retrieve precise architectural decisions or facts that weren't caught in the implicit prompt.
- You want to forcefully commit a new structural rule or fact to your `long_term` memory.

## Usage Guide

Instead of trying to manually open `memory.lance` (which is a complex Parquet/Vector structure), you will interact with the database using the following python script execution:

### 1. Deep Search Memory

If you want to search previous conversations or logs:

```bash
python -c "
import sys; sys.path.insert(0, '/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2')
from nanobot.agent.memory import MemoryStore
from pathlib import Path
m = MemoryStore(Path('/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2/workspace').expanduser())
results = m.search_memory('your search query here', limit=10)
for r in results:
    print(f\"[{r['timestamp']}] ({r['memory_type']}): {r['text']}\")
"
```

### 2. Force Rewrite Long Term Facts

If you learn something very important (like a user's API key path, or a new project constraint) that you want to be permanently available in the "Core Long-term Memory" section of your prompt forever:

```bash
python -c "
import sys; sys.path.insert(0, '/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2')
from nanobot.agent.memory import MemoryStore
from pathlib import Path
m = MemoryStore(Path('/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2/workspace').expanduser())
# Note: write_long_term completely overwrites the legacy MEMORY.md and adds a long_term LanceDB entry. 
# Make sure to append your new fact to the existing facts before writing.
m.write_long_term('''
# Long Term Facts
- User's preferred deployment target is GCP Cloud Run.
- The project follows a strict No-Typescript policy.
''')
"
```

### 3. Resolving Memory Contamination

If you realize that the `Implicit RAG` context is consistently injecting a bad, outdated, or hallucinated memory that is confusing you, you can permanently delete it by its `id`:

```bash
python -c "
import sys; sys.path.insert(0, '/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2')
from nanobot.agent.memory import MemoryStore
from pathlib import Path
m = MemoryStore(Path('/Users/kentchiu/.nanobot/workspace/openmemo/nanobot-2/workspace').expanduser())
rows_deleted = m.delete_memory(memory_id='the-uuid-string-from-search-results')
print(f'Deleted {rows_deleted} contaminated memories.')
"
```
