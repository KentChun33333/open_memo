---
title: "Understanding Nanobot's AgentLoop: Architecture, MCP, and Skills"
date: "2026-02-21"
tags: ["nanobot", "architecture", "agent", "mcp"]
slug: "nanobot-agent-loop-architecture"
---

# Understanding Nanobot's AgentLoop: Architecture, MCP, and Skills

The `AgentLoop` acts as the central cognitive engine of the Nanobot system. Operating on a **Pull Architecture**, it continually polls a `MessageBus` for inbound messages, processes them through a Large Language Model (LLM) to determine necessary actions, executes those actions using tools, and publishes the final output back to the bus.

This post provides a deep dive into the architecture of `AgentLoop.py`, how it uses the Model Context Protocol (MCP) to interact with external tools, and the workflow for handling custom agent skills.

---

## 1. High-Level Architecture

The `AgentLoop` brings together several distinct sub-systems:

- **LLM Provider** (`self.provider`): The intelligence engine responsible for processing prompts and making decisions about tool calls.
- **Tools Registry** (`self.tools`): A unified manager containing all available agent capabilities, including default tools (filesystem, web search) and dynamic tools (MCP).
- **Session Manager** (`self.sessions`): Tracks conversation history over the short term, organized uniquely by `channel` and `chat_id`.
- **Context Builder** (`self.context`): Continuously assembles the LLM's system prompt by aggregating persona details, skills, and memory.
- **Memory Store** (`self.memory`): Handles vector and markdown-based long-term memory retrieval and writes.

---

## 2. The Core Workflow

### A. The Ingestion Loop (`run` and `_process_message`)

When you execute `await agent.run()`, the agent starts an infinite asynchronous loop, waiting for messages via `self.bus.consume_inbound()`.

Upon receiving a message, the workflow is as follows:

1. **System & Command Handling**: Checks for system background messages or slash commands (like `/new` to flush session history).
2. **Context Routing**: Sets the `channel` and `chat_id` on stateful tools (like `MessageTool` or `SpawnTool`) so the agent knows precisely where to route its outgoing actions.
3. **Memory Consolidation Validation**: Checks if the short-term memory history exceeds the defined `memory_window`. If it does, an asynchronous task (`_consolidate_memory`) is fired off to summarize oldest messages into the long-term `MEMORY.md` file.
4. **Context Construction**: Assembles the user's new message, the session history, and system configurations into a strict prompt structure.

### B. The ReAct Execution Engine (`_run_agent_loop`)

This function serves as the "brain," implementing the classic **ReAct (Reason + Act)** loop pattern capped by a `max_iterations` guard (default 20) to prevent infinite loops.

```python
# Pseudo-code representation
msg_context = build_messages()
while iterations < max_iterations:
    response = LLM(msg_context, tools)
    
    if response.has_tool_calls:
        for tool in response.tool_calls:
            result = tools.execute(tool.name, tool.arguments)
            msg_context.append(result)
        
        msg_context.append("Reflect on the results and decide next steps.")
    else:
        return response.content
```

If the LLM triggers a tool call, the `AgentLoop` automatically intercepts it, runs the Python tool implementation, appends the string result back into the prompt history, and forces the LLM to process the result to determine its next move.

---

## 3. Handling MCP (Model Context Protocol) Tools

Nanobot seamlessly integrates external capabilities through the Model Context Protocol. Rather than hardcoding APIs, the `AgentLoop` connects to MCP servers and registers their tools dynamically.

### Connection Phase

In `_connect_mcp()`, the loop initializes an `AsyncExitStack` to manage the lifecycle of external processes. It connects to the configured MCP servers over `stdio` channels and dynamically extracts all available tools exposed by the server. These tools are injected into the unified `ToolRegistry` alongside native tools like `exec`.

### Execution Phase

Because MCP tools are registered directly into the `ToolRegistry`, the `AgentLoop` doesn't differentiate between them and native Python tools.

When the LLM requests an MCP tool (e.g., `github_get_issue`):

1. `_run_agent_loop` extracts the JSON payload and calls `self.tools.execute()`.
2. The `ToolRegistry` identifies it as an MCP tool and forwards the JSON-RPC request across the `stdio` boundary to the external server.
3. The server replies with the result, which is funneled back as a string to the `AgentLoop`, and ultimately back into the LLM's context window.

---

## 4. The Flow of Custom Skills

Custom skills in Nanobot extend the agent's capabilities via explicit instruction sets stored in `<workspace>/skills/<skill-name>/SKILL.md`.

Here is the exact flow of how `AgentLoop` and `ContextBuilder` handle these skills during prompt generation:

1. **Progressive Loading initiation:** The `ContextBuilder.build_system_prompt()` queries the `SkillsLoader` to partition skills.
2. **Always-On Skills (`always_on=true`):** If a skill is marked as `always_on`, the `ContextBuilder` opens the `SKILL.md` file and physically embeds the entire markdown instruction set directly into the LLM's system prompt prior to every message.
3. **Available Skills (`always_on=false`):** To preserve context window limits, the `ContextBuilder` does not inject the entire file for standard skills. Instead, it generates a summary dictionary mapping the skill's name to a short description.
4. **Agent Discovery and Usage:** The system prompt explicitly instructs the LLM: *"The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool."*
5. **Execution:** If the LLM determines a standard skill is required based on its summarized description, it will first generate a tool call to `read_file` targeting the skill's `SKILL.md`. Once the LLM reads the file's contents, it follows the explicit instructions—often utilizing the `exec` tool to run the companion Bash or Python scripts associated with that skill.

By combining native ReAct execution, universal MCP integration, and progressive contextual loading for custom skills, Nanobot achieves maximum flexibility and extensibility while strictly managing its token overhead.
