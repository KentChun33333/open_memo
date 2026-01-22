# MCP Agent Example

This directory contains an example of an **MCP (Model Context Protocol) Agent** that connects to a local MCP server to perform tasks.

## 🏗 System Architecture

The system consists of three main components:

1.  **MCP Agent (`main.py`)**: The intelligent orchestrator that uses an LLM (Large Language Model) to understand user queries and decide which tools to use.
2.  **MCP Agent Library (`mcp-agent`)**: The core framwork that handles the connection, tool discovery, and communication protocol.
3.  **Local MCP Server (`../mcp-server`)**: A separate process that exposes specific capabilities (tools) like trading calculations and sports statistics.

### 🔗 How the MCP Server is Hooked & Launched

The connection between the Agent and the Server is defined in **`mcp_agent.config.yaml`**.

```yaml
mcp:
  servers:
    my-local-tools:
      command: /opt/anaconda3/bin/python3
      args:
        - /path/to/mcp-server/my_custom_tools.py
```

**Auto-Launching Behavior:**
*   When you run `main.py`, the `mcp-agent` library reads this configuration.
*   It automatically **spawns a subprocess** for the defined server command (`python3 my_custom_tools.py`).
*   It establishes a **Standard IO (stdio)** connection with that process.
*   The agent then "handshakes" with the server to discover available tools (e.g., `calculate_position_size`, `get_match_history`).
*   When the agent finishes or crashess, it automatically terminates the server subprocess.

## 🧠 System Behavior

1.  **Initialization**:
    *   The Agent starts up and loads the `Nemotron-3-nano` model (via Ollama).
    *   It connects to `my-local-tools` and registers the available tools into its context.
    *   You will see logs indicating `Up and running with a persistent connection!`.

2.  **Query Processing**:
    *   A user asks a question (e.g., "What is my win rate?").
    *   The Agent sends this query + descriptions of available tools to the LLM.
    *   The LLM analyzes the request and decides if a tool is needed.

3.  **Tool Execution**:
    *   If the LLM selects a tool, the Agent sends a request to the local MCP server process.
    *   The server executes the Python function (e.g., reads `matches.csv`) and returns the result.
    *   The Agent feeds this result back to the LLM to generate the final natural language response.


## 🤖 Integrating with Ollama

The system is configured to use **Ollama** as the local LLM provider. This is handled via the **OpenAI Compatibility Layer** provided by `mcp-agent`.

### Configuration (`mcp_agent.config.yaml`)
To use Ollama, we configure the `openai` settings but point the `base_url` to your local Ollama instance:

```yaml
openai:
  api_key: ollama               # Required placeholder for the client
  base_url: http://localhost:11434/v1  # Point to Ollama's OpenAI-compatible endpoint
  default_model: Nemotron-3-nano       # The model successfully pulled in Ollama
```

> [!TIP]
> **Key Configuration Change**: The critical step is using the `openai` top-level key in `mcp_agent.config.yaml` and redirecting the `base_url`. This tricks the `mcp-agent` (which uses the OpenAI SDK) into talking to your local Ollama instance without needing any code changes in `main.py`.

### How it works
1.  **OpenAI Compatibility**: Using `OpenAIAugmentedLLM` allows us to leverage the standard OpenAI SDK inside the agent.
2.  **Model Routing**: By changing `base_url`, the SDK sends requests to `localhost:11434` instead of `api.openai.com`.
3.  **No Code Changes**: You don't need custom Python code for Ollama; just standard `OpenAIAugmentedLLM` with the right config.

## 🚀 Running the Example


```bash
# 1. Ensure Ollama is running
ollama serve

# 2. Run the agent
/opt/anaconda3/bin/python3 main.py
```
