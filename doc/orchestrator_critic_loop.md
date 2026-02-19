# Orchestrator Critic Loop

## Phase 1: Core Implementation (Completed)

### 1. New MCP Tools (`file_server.py`)

I added four new tools to enable robust verification and batch operations:

- **`read_files(paths)`**: Reads multiple files at once.
- **`write_files(files)`**: Writes multiple files at once.
- **`check_syntax(path)`**: Validates Python (AST) and JS/Node (node -c) syntax.
- **`validate_imports(path)`**: Scans code for imports and cross-references them with `package.json` (JS/TS) or `requirements.txt` (Python).

### 2. Orchestrator Critic Loop (`orchestrator.py`)

I modified the main execution loop to include a **Critic Phase** after every technical step.

- **`_run_critic_phase`**: Spawns a dedicated "Technical-Critic" agent.
- **Workflow**:
    1. Worker completes task.
    2. Verifier checks physical existence.
    3. **Critic** audits code quality and dependencies.
    4. If Critic fails the step, the Worker is forced to retry with feedback.

### 3. Prompt Hooks (`prompt.py`)

I updated the `SUBAGENT_INSTRUCTION` to include a **Self-Correction Checklist**, explicitly reminding the agent to:

- Check dependencies (`package.json`).
- Verify syntax.
- Confirm file writes.

## Phase 2: Refinements & Telemetry (Completed)

### 4. Structured Handover (`structs.py`)

Created `CriticHandover` dataclass to serialize context into XML.

```xml
<CriticContext>
  <StepID>...</StepID>
  <WorkerOutput>...</WorkerOutput>
  <ProjectRoadmap>...</ProjectRoadmap>
</CriticContext>
```

### 5. Telemetry Integration

Added structured logging events:

- `CRITIC_START`: Logs when the audit begins.
- `CRITIC_DECISION`: Logs [APPROVED] or [REJECTED] and the feedback snippet.

### 6. Centralized Prompts

Moved the massive Critic Instruction to `prompt.py` as `CRITIC_INSTRUCTION` to keep `orchestrator.py` clean.

## Verification Results

### Automated Tool Verification

- `test_tools_manual.py`: Verified `check_syntax` and `validate_imports` logic.
- `test_refined_critic.py`: Verified `CriticHandover` XML generation.

### Manual Verification Steps for User

To verify in the full agent loop:

1. Run the agent with a coding task:

   ```bash
   python3 mcp_skill_agent/main_v3.py "Create a script using requests"
   ```

2. Observe the logs. You should see:
   - `[Orchestrator] Invoking Technical Critic...`
   - Telemetry logs for `CRITIC_START`.
   - `[Critic Feedback]: ...`
   - If `requests` is missing, the Critic should flag it.
