# Advanced Agent Architecture: Antigravity vs MCP Agent

This document analyzes the gap between high-level agents (like Antigravity/Claude Code) and the default `mcp-agent` flow, and proposes an enhanced architecture for [main.py](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/main.py).

## Comparison

| Feature | Antigravity / Claude Code | Default `mcp-agent` |
| :--- | :--- | :--- |
| **Lifecycle** | **Stateful Loop**: Plan → Execute → Verify → Report | **Single Shot**: Request → React Loop → Final Answer |
| **Planning** | Explicit [task.md](file:///Users/kentchiu/.gemini/antigravity/brain/35ea3133-9dcc-4dee-a15b-6b961100371c/task.md) / Checklist. Tasks are tracked and updated. | Implicit / Hidden in Chain of thought. No persistent artifact. |
| **Context** | Active Context Management (Read specific files, search codebase). | Passive. Relies on what's injected in prompt. |
| **Persistence** | Writes state to disk (Artifacts). Can resume. | In-memory only. Lost on exit. |
| **Tooling** | "Meta-tools" (Task Boundary, Artifacts) + Domain Tools. | Domain tools only. |

## The "Missing Link" in [main.py](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/main.py)

The current [main.py](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/main.py) uses a simple `llm.generate_str(query)` call. This relies entirely on the LLM's internal "Chain of Thought" to manage complexity. For multi-step tasks (like "Init project" -> "Write Code" -> "Bundle"), one-shot execution often fails because:
1.  **Context Window Pressure**: The model forgets earlier steps or specific requirements.
2.  **Premature Completion**: The model sees "Init done" and thinks "I'm done" without realizing it needs to bundle.
3.  **Lack of Structure**: No visible checklist to enforce completion.

## Proposed Architecture: The "Plan-Execute" Loop

We will enhance [main.py](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/main.py) to implement a simplified version of the Antigravity loop.

### 1. explicit Planning Phase
Before running tools, the agent must generate a **Plan**.
-   **Input**: User Query.
-   **Output**: A structured checklist (Markdown).

### 2. Execution Loop
The agent iterates through the plan.
-   **Input**: Current Plan + History.
-   **Action**: Execute next step.
-   **Constraint**: Use [activate_skill](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/skill_server.py#21-30) for domain knowledge.

### 3. Verification
Explicit verification step before finishing.

## Implementation Details for [main.py](file:///Users/kentchiu/Documents/Github/open_memo/mcp_skill_agent/main.py)

We will split [main()](file:///Users/kentchiu/Documents/Github/open_memo/.agent/skills/skill-creator/scripts/init_skill.py#273-300) into explicit stages:

```python
async def main(query):
    # Setup ...
    agent = Agent(...)
    
    # 1. PLANNING
    print("🧠 Generating Plan...")
    plan_prompt = f"Goal: {query}\n\nCreate a numbered checklist of steps to achieve this goal using available skills."
    plan = await agent.llm.generate_str(plan_prompt, force_no_tools=True) # Conceptual
    print(f"Plan:\n{plan}")
    
    # 2. EXECUTION
    print("🛠️ Executing Plan...")
    execution_prompt = (
        f"Goal: {query}\n"
        f"Approved Plan:\n{plan}\n\n"
        "Execute this plan step-by-step. "
        "Do not skip steps. Verify each step."
    )
    result = await agent.llm.generate_str(execution_prompt)
    print(f"Result:\n{result}")
```

*Note: If `mcp-agent` doesn't support `force_no_tools`, we can just instruct it "DO NOT use tools yet, just plan".*
