# Deep Analysis: Why the Web Artifacts Builder Agent Fails

You observed that your `mcp_skill_agent` successfully initializes the project (runs `scripts/init-artifact.sh`) but fails to "Develop" it (customize the code), leaving you with just the template. In contrast, robust agents like `antigravity` or `claude-code` succeed.

Here is the root cause analysis and the solution.

## 1. The "Blind Programmer" Problem

**The core failure condition is "Blindness".**

1. **Missing Exploration Tools**:
    - Your agent prompt *claims* to have `list_directory`, but the actual `fs_server.py` implementation **DOES NOT** have this tool.
    - **Result**: After running `init-artifact.sh`, the agent is blindly guessing where the files are. It cannot run `ls` or `tree` to see the generated `src/App.tsx` or `src/components`. It doesn't know what files exist to edit.

2. **Missing "read-before-write" Loop**:
    - Effective agents (like Antigravity) follow a loop: `Explore` -> `Read` -> `Think` -> `Edit`.
    - Your subagent is told to "Develop your artifact", but without `list_directory`, it skips the "Explore" phase. It likely hallucinates path names or simply gives up because it can't "see" the code it just created.

## 2. The "Blunt Instrument" Problem

**The second failure is "Lack of Precision".**

1. **No Code Modification Tool**:
    - `fs_server.py` only implements `write_file`, which overwrites the *entire* file.
    - To change one line in `App.tsx`, the LLM must perfectly hallucinate/reproduce the entire 50-line file with zero context. This is highly error-prone for smaller models (like Nemotron-3-nano).
    - **Required**: A `replace_string` or `apply_patch` tool is essential. This allows the agent to say "Change `<h1...>` to `<h1>My Custom Title</h1>`" without rewriting the whole file.

## 3. The "State Amnesia" Problem

**The third failure is "Context Isolation".**

1. **No Feedback Loop**:
    - When `init-artifact.sh` runs, it outputs a lot of logs. But the agent doesn't necessarily "ingest" the file structure from those logs into its "Mental Map" for the next step.
    - Advanced agents run `ls -R` immediately after avoiding "amnesia" about the file state.

---

## Proposed Solution: The "Developer Toolpack" Upgrade

To fix this, we need to upgrade `fs_server.py` to give the agent "Vision" and "Surgical Hands".

### Step 1: Upgrade `fs_server.py`

Add these three tools:

1. `list_directory(path)`: (CRITICAL) Allows the agent to see the project structure.
2. `search_files(pattern)`: (Recommended) Simple grep to find text like "Edit this text".
3. `replace_in_file(path, search, replace)`: (CRITICAL) "Surgical" editing. Much easier for LLMs than full file overwrites.

### Step 2: Update Subagent Instruction

Update `SkillManager` to verify that the agent *explores* before editing.

- Add to prompt: "After running a script that generates files, you MUST use `list_directory` to verify the structure before editing."

### Step 3: (Advanced) RAG / LSP

- **RAG**: You asked about RAG. While helpful, it's *secondary*. The agent doesn't need to know every shadcn API perfectly to make *some* edit. It first needs to simply *see* the file to edit it.
- **LSP**: Adding a Language Server is complex. Start with basic `list` + `read` + `replace`. That is sufficient for 90% of tasks.

## Next Steps

I recommend we implement the **Developer Toolpack** (Step 1) immediately.
