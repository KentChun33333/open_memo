# Deep Research: Why Clawdbot Follows Steps Better than mcp_skill_agent

## Executive Summary

**Clawdbot** enables superior adherence to step-by-step instructions through a **"Pull" architecture** (Agent actively retrieves skills as tools) and a **State-Aware Prompting System** that includes runtime context (time, capability, identity).

**mcp_skill_agent** uses a **"Push" architecture** (Planner forces skill text into System Prompt). While simpler, this overwhelms the context window upfront and lacks the "cognitive round-trip" that occurs when an agent must actively read and interpret a skill file.

## 1. Architectural Difference: Pull vs. Push

### Clawdbot (The "Pull" Model)

* **Discovery**: The system prompt lists *descriptions* of skills but NOT their full content.
* **Action**: The agent must decidingly call a tool (e.g., `read_skill("web-artifacts-builder")`) to get instructions.
* **Result**:
    1. **Cognitive Break**: The agent pauses to read. The act of calling the tool reinforces intent.
    2. **Fresh Context**: The instructions arrive as a *Tool Output* (Observation), which LLMs often prioritize over static System Prompts.
    3. **Step-by-Step State**: The agent is naturally in a "reading -> planning -> executing" loop.

### mcp_skill_agent (The "Push" Model)

* **Discovery**: The Planner decides the skill.
* **Action**: The `main.py` script retrieves the *entire* skill content (HTML, Scripts, references) and injects it into the Subagent's System Prompt *before* the first turn.
* **Result**:
    1. **Context Overload**: The agent starts with a massive block of text (the skill).
    2. **Lost Focus**: Without the active step of "reading" the skill, the agent treats it as background noise rather than active instructions.
    3. **hallucination**: It often assumes it knows what to do without verifying the specific steps 1, 2, 3.

## 2. Prompt Engineering & Context

### Clawdbot's System Prompt (`system-prompt.ts`)

* **Dynamic Construction**: Builds prompt based on *Runtime State* (Time, OS, Capabilities).
* **Explicit Constraints**: *"Constraints: never read more than one skill up front; only read after selecting."*
* **Tool-Native**: Defines tools clearly with `coreToolSummaries` and enforces specific usage patterns (e.g., "Narrate only when it helps").

### mcp_skill_agent's Prompt (`main.py`)

* **Static Injection**: Appends `skill_manager.get_skill_instruction(name)` + some fixed rules.
* **Loop Weakness**: Relies on `mcp_agent.run_loop` (implied `generate_str` loop). If the underlying library doesn't strictly enforce Thought/Action pairs, the model rushes to the final answer.

## 3. Tooling Gaps (Addressed in recent update)

* **Before**: `mcp_skill_agent` lacked stateful bash (no `cd`) and surgical editing.
* **Now**: We added `bash_tools` (Editor, Persistent Shell).
* **Remaining Gap**: The *Agent Logic* doesn't fully utilize them yet. It needs to "feel" the state.

## Recommendation

To make `mcp_skill_agent` match Clawdbot's reliability, we should **mimic the Pull Model**:

1. **Don't inject the full skill.** Give the Subagent the `Skill Name` and a tool `read_skill_instruction()`.
2. **Force the "Read" Step.** In the initial user prompt, say: *"Task: X. First, use `read_skill_instruction` to get the steps."*
3. **Enforce Verification.** Use a loop that explicitly checks: *"Have I completed Step X?"* before moving on.
