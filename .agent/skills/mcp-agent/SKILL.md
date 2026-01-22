---
name: mcp-agent
description: Utilities for running and managing MCP Agents. Use this skill when the user wants to creating agents or interact with MCP servers using the `mcp-agent` library.
---

# MCP Agent Skill

This skill provides guidance and tools for working with the `mcp-agent` library to build and run AI agents that can connect to MCP servers.

## When to use

Use this skill when:
- Creating new MCP agents.
- configuring `mcp-agent` to connect to local or remote tools.
- Orchestrating multi-agent systems using `mcp-agent`.

## Usage

### 1. Configuration

Agents are configured via YAML files (e.g., `mcp_agent.config.yaml`).

```yaml
mcp:
  servers:
    my-server:
      command: python3
      args:
        - /path/to/server.py
openai:
  api_key: ollama
  base_url: http://localhost:11434/v1
  default_model: Nemotron-3-nano
```

### 2. Basic Agent Template

To create a simple agent that uses these tools:

```python
import asyncio
import os
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

# Start the app
app = MCPApp(name="my_agent", settings="path/to/config.yaml")

async def main():
    async with app.run():
        agent = Agent(
            name="helper",
            instruction="You are a helpful assistant.",
            server_names=["my-server"], # Must match config
        )
        async with agent:
            # Attach LLM
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            # Run Query
            response = await llm.generate_str("Your Query Here")
            print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

- **Configuration Management**: context usually dictates where `mcp_agent.config.yaml` lives. Ensure paths in the config are absolute.
- **Server names**: `server_names` in `Agent` constructor must exactly match the keys in `mcp.servers` in the config YAML.
- **Model selection**: If using Ollama, ensure `default_model` in config matches a model that supports tool calling if possible, or use a robust model.
