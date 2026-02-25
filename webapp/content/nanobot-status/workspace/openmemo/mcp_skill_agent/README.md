# MCP Skill Agent

This project demonstrates how to implement the **Agentskill Protocol** using the vanilla `mcp-agent` library. It enables an AI agent to dynamically discover, learn, and use "Skills" by leveraging the "Progressive Disclosure" pattern.

## Core Implementation: Progressive Disclosure

To manage context window efficiency while providing access to vast capabilities, this implementation uses a 3-stage loading pattern:

### Level 1: Awareness (Metadata)
*   **What it is**: A high-level list of skill names and descriptions.
*   **Implementation**: `SkillManager` scans `.agent/skills/` and parses YAML frontmatter from `SKILL.md` files.
*   **Usage**: In `main.py`, this list is injected into the System Prompt. The agent knows *what* skills exist but not *how* to use them detailedly.
*   **Benefit**: Hundreds of skills costs almost zero tokens.

### Level 2: Activation (Instructions)
*   **What it is**: The full instructional content of a skill.
*   **Implementation**: `skill_server.py` exposes the `activate_skill` tool.
*   **Usage**: The agent calls `activate_skill(name)`. The server returns the full markdown body of `SKILL.md`, which contains the specific "how-to".
*   **Benefit**: Detailed instructions are loaded only when actually needed.

### Level 3: Execution (Resources & Scripts)
*   **What it is**: Executable scripts and reference documents bundled with the skill.
*   **Implementation**: specialized tools in `skill_server.py`:
    *   `list_skill_contents`: Shows available scripts/references.
    *   `read_skill_reference`: Reads text files (e.g., API docs).
    *   `run_skill_script`: Executes Python/Bash scripts securely in the skill's directory context.
*   **Usage**: The agent discovers and uses these assets to perform complex tasks or retrieve static knowledge without hallucination.

## Architecture

The system consists of three main components:

1.  **Skill Manager** (`skill_manager.py`):
    *   **Role**: The "Brain" of the skill system.
    *   **Functions**: Path resolution, frontmatter parsing, recursive logic, and safe execution wrappers.

2.  **Skill Loader Server** (`skill_server.py`):
    *   **Role**: The "Bridge" (MCP Server).
    *   **Tech**: Uses `FastMCP` to quickly wrap `SkillManager` methods as standardized MCP tools.
    *   **Tools Exposed**: `activate_skill`, `list_skill_contents`, `read_skill_reference`, `run_skill_script`.

3.  **Skill-Aware Agent** (`main.py`):
    *   **Role**: The "User".
    *   **Tech**: Uses `mcp-agent` library.
    *   **Lifecycle**:
        1.  Initializes `SkillManager` locally to generate the dynamic System Prompt.
        2.  Connects to `Skill Loader Server` (defined in `config.yaml`).
        3.  Processes user queries, autonomously deciding when to "activate" a skill or run a script.

## Directory Structure

```
mcp_skill_agent/
├── main.py           # The agent orchestration script
├── skill_manager.py  # Core logic for scanning and reading skills
├── skill_server.py   # FastMCP server exposing skill tools
├── config.yaml       # Configuration linking Agent to Server
└── README.md         # Documentation
```

## How to Run

1.  **Prerequisites**: Ensure `mcp-agent` and `fastmcp` are installed and you have an Ollama instance running.
2.  **Execution**:
    ```bash
    python mcp_skill_agent/main.py
    ```

## Adding New Skills

The agent automatically discovers new skills. To add one:
1.  Create `.agent/skills/<your-skill-name>/SKILL.md`.
2.  Add the required YAML frontmatter:
    ```yaml
    ---
    name: your-skill-name
    description: When to use this skill...
    ---
    ```
3.  (Optional) Add `scripts/` or `references/` directories for Level 3 support.
