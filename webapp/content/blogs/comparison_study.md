---
title: "Comparison Study: Agent vs. Professional Design Requirements"
date: "2025-02-04"
tags: ["comparison", "production", "gap-analysis"]
---

# Comparison Study: Current Agent vs. Professional Design Requirements

This report analyzes the gap between the current `mcp_skill_agent` implementation (specifically `main_prod.py` and `orchestrator.py`) and the "Top 10 Must-Have Design Requirements" for industrial agents.

## 1. Executive Summary

The current implementation is a functional **Prototype (Level 3)**. It has a solid foundation with SOP guidance (`SOPAgent`), basic memory (`SessionMemoryManager`), and verification (`Verifier`), but it lacks the resilience, state management, and safety features required for a **Production (Level 5)** system.

The most critical missing pieces are **State Persistence (Hydration)**, **Fine-Grained Error Reconciliation**, and **Telemetry**.

## 2. Detailed Gap Analysis

| Requirement | Current Status | Analysis of `main_prod.py` / `orchestrator.py` |
| :--- | :--- | :--- |
| **1. State Checkpointing** | ⚠️ Partial | **Existing:** `SessionMemoryManager` saves `.agent_state.json`.<br>**Missing:** Comprehensive "Hydration". If the script crashes, you can restart from the persistent state file, but the `Orchestrator.run()` loop doesn't have explicit logic to "resume" a specific step ID from disk upon startup. It always starts at Phase 1 (Planning). |
| **2. Deterministic Checks** | ✅ Implemented | **Existing:** `Verifier.verify_artifacts()` is called after every step execution (Line 131). This checks for the physical existence of files. <br>**Note:** Implementation is good, but based on the previous failure, the *granularity* of checks (e.g., checking imports inside files) is missing. |
| **3. Capability Scoping** | ❌ Missing | **Existing:** All agents seem to share the same broad set of tools (`file-tools`, `skill-server`).<br>**Missing:** No logic in `Orchestrator` to restrict specific tools for specific SOP steps (e.g., locking `run_skill_script` only to Execution phase). |
| **4. Structured Handover** | ⚠️ Partial | **Existing:** `SOPAgent` tracks state, but the handover between "Planner" and "Executor" is just a string regex match (Lines 197-201).<br>**Missing:** A formal JSON schema passed between agents containing environment vars or active context. |
| **5. Token Pruning** | ❌ Missing | **Existing:** `SessionMemoryManager` appends logs indefinitely (`logs` list in `session_memory.py`).<br>**Missing:** No "Auto-Summarizer" or context window management logic seen in `Orchestrator`. Long sessions will crash due to token limits. |
| **6. Error-Reconciliation** | ❌ Missing | **Existing:** The "Retry Loop" (Lines 118-165) simply re-runs the exact same step with a generic error message ("VALIDATION ERROR").<br>**Missing:** No logic to feed *stderr* back to the agent with a specific "Self-Correction" prompt. It just says "Try again". |
| **7. Atomic Task Decomposition** | ✅ Implemented | **Existing:** `SOPAgent` and `StepExecutor` enforce a step-by-step workflow. The `while not sop.is_finished()` loop (Line 88) is a strong FSM implementation. |
| **8. Telemetry & Auditing** | ❌ Missing | **Existing:** Basic `logger.info` and print statements.<br>**Missing:** No centralized structured logging (JSON logs) tracing Thought -> Action -> Result for debugging historical decisions. |
| **9. Latency (Parallelism)** | ❌ Missing | **Existing:** The `StepExecutor` appears to run sequentially.<br>**Missing:** No batch execution logic (e.g., `asyncio.gather` for multiple independent file writes). |
| **10. HITL Breakpoints** | ❌ Missing | **Existing:** Completely autonomous loop. Warns about Context Switches (Line 103) but doesn't stop.<br>**Missing:** No `input("Press Enter to continue...")` or API pause mechanism before destructive actions. |

## 3. High-Priority Research & Action Plan

Based on the analysis, here is the recommended plan to bridge the gap from Prototype to Production.

### Phase 1: Stability & Resilience (The "Crash Proofing")

* **Research:** `pydantic` for strict state serialization.
* **Action:** Upgrade `SessionMemoryManager` to support full **Hydration/Dehydration**.
  * *Goal:* If I `Ctrl+C` the agent at Step 3, running `python main_prod.py` should ask: "Detected unfinished session at Step 3. Resume? [Y/n]"

### Phase 2: Intelligence Upgrade (The "Self-Healer")

* **Research:** "Reflexion" patterns for agents.
* **Action:** Implement **Error-Reconciliation Loops**.
  * *Goal:* When a tool fails (stderr), the Orchestrator should capture the error and inject it into the *next* prompt with: "Last attempt failed with [Error]. Please fix current file." instead of just retrying.

### Phase 3: Safety & Governance (The "Guardrails")

* **Research:** RBAC (Role-Based Access Control) for LLM Tools.
* **Action:** Implement **Capability Scoping**.
  * *Goal:* The "Planner" agent should NOT have write access to the filesystem. The "Writer" agent should NOT have access to `rm -rf`.

### Phase 4: Production Readiness

* **Action:** Implement **Token Pruning**. Use a sliding window for logs or summarized history context.
* **Action:** Add **HITL Breakpoints** for specific dangerous tools (e.g., `bundle-artifact.sh`).

## 4. Conclusion

The current `main_prod.py` is a strong "Happy Path" executor. It works well when everything goes right. However, it fails the "Production Test" because it treats errors as fatal (or blindly retries) and assumes perfect continuity. Adopting requirements #1 (Persistence) and #6 (Reconciliation) will yield the highest immediate ROI.
