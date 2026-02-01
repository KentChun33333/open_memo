In modern, production-grade agentic systems, we move away from "passing strings" and toward a "State-Centric Architecture." In this design, the agents do not own the memory; the Platform (Orchestrator) owns the memory, and agents "borrow" it through a structured Session Context.

Here is the industrial blueprint for managing complex, multi-agent communication.

1. The "Blackboard" Architecture (Shared State)
Instead of Agent A talking directly to Agent B (which causes "telephone game" data loss), every agent reads from and writes to a central Blackboard (the SessionMemory).

The 5 Pillars of the Shared State:
Entity Memory (The "What"): Tracks artifacts (e.g., package.json, App.tsx) and their absolute paths.

Environmental State (The "Where"): The active_project_dir. This is the "Anchor" that ensures no agent gets lost.

Instructional History (The "How"): The SOP progress (which steps are done).

Tool Trace (The "Action"): A log of every tool execution and its success/failure.

Critique Log (The "Quality"): Feedback from the Critic Agent that needs to be addressed by the Worker.

2. Structured Handover: The "Envelope" Pattern
In production, you never send a raw string to a subagent. You wrap the task in a Context Envelope. This ensures the Critic or the Developer knows the ground truth before they start.

The Handover Schema (Example):
JSON
{
  "header": {
    "sender": "Orchestrator",
    "recipient": "CriticAgent",
    "timestamp": "2026-02-01T10:25:23Z"
  },
  "payload": {
    "task": "Review App.tsx",
    "active_dir": "/abs/path/to/project",
    "last_tool_output": "Successfully wrote to src/App.tsx",
    "expected_artifacts": ["bundle.html"]
  },
  "history_summary": "Step 1 (Init) succeeded. Step 2 (Code) just finished generation."
}
3. Best Practices for State Management
A. The "Path Anchor" Rule
Never use relative paths in shared memory. The Orchestrator should convert every path to an Absolute Path before storing it in the active_project_dir. This prevents "Blindness" if one agent uses a tool that starts in a different subshell.

B. The "Snapshot" Principle
Before a specialized agent (like the Critic) starts its turn, the Orchestrator takes a Snapshot of the filesystem or the task.md.

Why: If the Critic finds a bug and the Worker fails to fix it, you can "Rollback" the state to the snapshot instead of having a broken project.

C. Tiered Logging (Telemetry)
Don't mix "Agent Thoughts" with "Tool Results" in the same log file.

Trace Log: Raw tool calls and returns (for debugging).

Conversation Log: Thoughts and messages (for UX/UI).

State Change Log: Changes to the active_dir or artifacts (for the Orchestrator's logic).

4. Modern Production Design: The "Controller-Worker" Model
In mcp_agent, the most robust design is to have one Controller Agent that remains "alive" for the whole session, and many Ephemeral Worker Agents that are spawned and killed for single tasks.

The Lifecycle:
Controller: Maintains the SessionMemory.

Handover: Controller spawns a Worker, passes the "Envelope."

Execution: Worker performs the task, uses tools.

Report: Worker returns a Structured JSON Response (not just text).

Verification: Controller validates the response against the disk.

Cleanup: Worker is deleted; Controller updates the SessionMemory.

5. Top 5 Best Practices for Multi-Agent Communication
JSON-First Communication: Force agents to respond in JSON for status updates. It makes the Orchestrator's job 100% more reliable than regex.

Atomic Tool Scoping: Use the Registry Pattern to ensure the Critic cannot run write_file. Only the Worker has "Write" access.

Context Pruning: Every 5 turns, have the Orchestrator summarize the "Discussion History" so the context window stays small and the "Active Path" remains at the bottom of the prompt (the highest priority area).

Implicit Context Injection: Instead of telling the agent cd folder, the Tool itself should read the active_dir from the Session Memory and apply it.

Idempotent SOP: Every step should be re-runnable. If the Critic fails Step 2, the Orchestrator should be able to reset the active_dir and try again without breaking Step 1.

Next Step

To implement this in your orchestrator.py, would you like me to show you how to build the "Handover Envelope" Generator that automatically packages the SessionMemory into a clean prompt for the subagents?