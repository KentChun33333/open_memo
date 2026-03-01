---
name: "memory"
description: "Spawn a memory subagent to explicitly query LanceDB for historical depth, or memorize critical long-term facts cleanly."
---

# memory

This skill allows you to safely interact with the `memory.lance` backend database for cases where the implicit short-term context injected into your system prompt is not enough.

Because raw database results (like matching 50 historical records) will easily clutter your context window and slow you down, **you must never query memory yourself.** Instead, you will orchestrate a dedicated Memory Synthesis Subagent.

You should use this skill when:
- You need to search far back into conversation history (>3 turns).
- You want to retrieve precise architectural decisions or facts that weren't caught in the implicit prompt.
- You want to forcefully commit a new structural rule or fact to your `long_term` memory.


## Usage Guide

Instead of writing Python scripts, you will use your `spawn_subagent` tool to create a worker. The worker has exclusive access to atomic JSON database tools (`search_memory`, `write_memory`, `delete_memory`).

### 1. Deep Search Memory

If you want to search previous conversations or logs, spawn a subagent with a clear analytical task:

```json
{
  "task": "Use your search_memory tool to find any mentions of the 'OCBC' API deployment architecture. Read through the results and synthesize a single clean summary of the final decision. Announce only that summary.",
  "label": "Researching OCBC architecture"
}
```

### 2. Force Rewrite Long Term Facts

If you learn something very important (like a user's API key path, or a new project constraint) that you want to be permanently available in the "Core Long-term Memory" section of your prompt forever:

```json
{
  "task": "Use your search_memory tool to read the current long-term facts. Then, use your write_memory tool to append the following new fact: 'User's preferred deployment target is GCP Cloud Run.' Do not overwrite existing facts without merging them.",
  "label": "Updating GCP deployment preference"
}
```

### 3. Resolving Memory Contamination

If you realize that the `Implicit RAG` context is consistently injecting a bad, outdated, or hallucinated memory that is confusing you, you can permanently delete it by its `id`:

```json
{
  "task": "Use your search_memory tool to locate the exact memory_id of the hallucinated fact about 'TypeScript'. Then use your delete_memory tool to permanently remove it.",
  "label": "Purging hallucinated TypeScript fact"
}
```

**CRITICAL RULES:**

- Do not attempt to write Python (`ExecTool`) scripts to interact with memory.
- The subagent will do all the noisy data filtering and return only the clean, synthesized answer back to you.
