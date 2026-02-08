import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams

from ..utils.telemetry import get_telemetry
from ..handler.memory_handler import SessionMemoryManager
from ..prompt import INSTRUCTION_POOL, SUBAGENT_INSTRUCTION, USER_DYNAMIC_CONTEXT_TEMPLATE, AUTO_WRITE_PROMPT, GENERAL_SKILL_PROTOCOL
from .structs import StepExecutorInput, StepExecutorOutput, SkillStep, TechLeadInput # Explicit import

# Initialize Logger
logger = get_telemetry("step_executor")

class StepExecutor:
    """
    Controller Component: Step Execution Manager.
    - Manages the lifecycle of a single SOP step.
    - Spawns an EPHEMERAL Worker Agent.
    - Runs the ReAct loop.
    """
    def __init__(self, memory_manager: SessionMemoryManager, telemetry: Any = None):
        self.memory_manager = memory_manager
        self.telemetry = telemetry
        self.max_react_steps = 15 # Configurable?

    async def execute(self, 
                      current_step: SkillStep, 
                      task_input: str, 
                      skill_name: str, 
                      retry_feedback: str = "",
                      attempt_idx: int = 0) -> StepExecutorOutput:
        """
        Executes a single attempt of a step.
        """
        # 2. Build Handover Envelope (Protocol Layer)
        handover = self._build_worker_context(
            current_step=current_step,
            task_input=task_input,
            retry_feedback=retry_feedback
        )

        # 3. Construct System Prompt (Dynamic Persona)
        
        # Default Persona
        current_persona = "DEFAULT"
        subagent_instruction = self._build_system_instruction(handover)
        

        self.telemetry.log_event(
            event_type="STEP_START",
            step_id=current_step.id,
            details={"title": current_step.title, "attempt": attempt_idx, "persona": current_persona}
        )

        # 3. Spawn Ephemeral Agent
        worker_name = f"Worker-{skill_name}-{current_step.id}-{attempt_idx}"
        worker = Agent(
            name=worker_name,
            instruction=subagent_instruction,
            server_names=["file-tools"] 
        )

        logger.info(f"Spawning Worker: {worker_name} in {handover.active_folder}")



        final_response = ""
        success_signal = False
        
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            
            # Initial User Prompt (Simplified Trigger)
            user_prompt = self._build_initial_user_prompt(current_step, handover)
            
            # 4. ReAct Loop (Smart Loop)
            react_max_cycles = 15 
            cycle = 0
            
            while cycle < react_max_cycles:
                cycle += 1
                try:
                    # The Agent's internal generate_loop handles tool calls (up to 15 iterations)
                    response = await llm.generate_str(user_prompt, RequestParams(max_iterations=self.max_react_steps))
                    final_response = response
                    
                    # We inspect the agent's recent history to find tool calls
                    current_cycle_tools = [] # List of (name, args)
                    try:
                        # Inspect recent messages in worker history
                        history_source = getattr(worker, "history", []) or getattr(llm, "history", [])
                        if hasattr(history_source, "messages"): 
                             history_source = history_source.messages
                        
                        if not isinstance(history_source, list):
                             # Log type for debugging but default to empty to allow flow to continue
                             logger.debug(f"History source is not a list: {type(history_source)}")
                             history_source = []
                        
                        # Look at the last few messages (since we just ran generate_str)
                        for msg in history_source[-5:]: 
                            if hasattr(msg, "role") and msg.role == "assistant":
                                if hasattr(msg, "tool_calls") and msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        t_name = tc.function.name if hasattr(tc, "function") else str(tc)
                                        t_args = {}
                                        try:
                                            if hasattr(tc, "function") and tc.function.arguments:
                                                t_args = json.loads(tc.function.arguments)
                                        except Exception:
                                            pass
                                        current_cycle_tools.append((t_name, t_args))
                    except Exception as e:
                        logger.warning(f"Failed to extract tool usage: {e}")

                    # --- New: Capture Read Results for Persistence ---
                    self._capture_read_results(history_source)
                    
                    # Log to Session Memory
                    for t_name, t_args in current_cycle_tools:
                        self.memory_manager.log_tool_usage(
                            agent_name=worker_name,
                            step_id=current_step.id,
                            cycle=cycle,
                            tool_name=t_name,
                            args=t_args
                        )
                    
                    logger.debug(f"[{worker_name}] Cycle {cycle} Output: {response[:100]}...")
                    # ...
                    
                    # --- JSON Protocol Check ---
                    import re
                    # Look for JSON block first
                    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
                    json_str = ""
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        # Try to find brace-enclosed region
                        brace_match = re.search(r"(\{.*\})", response, re.DOTALL)
                        if brace_match:
                            json_str = brace_match.group(1)

                    if json_str:
                        try:
                            data = json.loads(json_str)
                            if data.get("status") == "success":
                                logger.info(f"[{worker_name}] Success Signal Received via JSON.")
                                success_signal = True
                                # Don't break immediately, let loop allow final check or just break next turn
                                break 
                        except json.JSONDecodeError:
                            logger.warning(f"[{worker_name}] Invalid JSON Detected.")
                            
                    # --- Intervention: Auto-Write (The "Catch-All") ---
                    if "```" in response and "write_file" not in response and not success_signal:
                        pass
                        
                except Exception as e:
                    logger.error(f"[{worker_name}] Error in Cycle {cycle}: {e}")
                    final_response += f"\nError: {e}"
                    break
        
        # 5. Return Result
        return StepExecutorOutput(
            success=success_signal, 
            output=final_response
        )



    def _build_system_instruction(self, handover: StepExecutorInput) -> str:
        """
        Constructs the System Prompt using the appropriate Persona.
        """
        # Default Persona (Future: Select based on step type)
        base_instruction = INSTRUCTION_POOL["DEFAULT"]
        
        return base_instruction.format(
            skill_manual_xml=handover.to_system_protocol_view(),
            general_skill_protocol=GENERAL_SKILL_PROTOCOL
        )

    def _build_initial_user_prompt(self, current_step: SkillStep, handover: StepExecutorInput) -> str:
        """
        Constructs the initial user message trigger.
        Reinforces task context (Recency Bias).
        """
        return handover.to_user_status_view(
            USER_DYNAMIC_CONTEXT_TEMPLATE, 
            step_id=current_step.id,
            step_title=current_step.title
        )

    def _build_worker_context(self, current_step: SkillStep, task_input: str, retry_feedback: str, max_context_length: int = 8000) -> StepExecutorInput:
        """
        Factory Method: Constructs the execution context for the worker.
        Encapsulates all logic for snapshotting, filtering, and side-channel injection.
        
        Args:
            max_context_length: Maximum character length for the skill context. Default 8000 chars (~2000 tokens).
        """
        # 1. Prepare Environment Snapshot (Stateless)
        active_folder = self.memory_manager.memory.active_folder
        session_snapshot = {
            "artifacts": self.memory_manager.memory.artifacts,
            "env_vars": self.memory_manager.memory.env_vars
        }
        session_context = json.dumps(session_snapshot, indent=2)
        
        # 2. Generate SOP Context (Progress Tracker)
        sop_context = "Task List:\n"
        plan = self.memory_manager.get_plan()
        if not plan:
             sop_context += "(No Plan Found in Memory)\n"
        else:
             for s in plan:
                 s_id = s.get("id")
                 s_title = s.get("title")
                 s_status = s.get("status")
                 mark = "[ ]"
                 if s_id < current_step.id: mark = "[x]"
                 elif s_id == current_step.id: mark = "[/]"
                 elif s_status == "done": mark = "[x]"
                 sop_context += f"{mark} {s_title}\n"

        # 3. Context Optimization (Working Set Policy)
        # Fetch only files accessed in recent history to save tokens
        recent_paths = self.memory_manager.get_recent_file_paths(lookback_steps=2)
        filtered_clipboard = self.memory_manager.get_clipboard_subset(recent_paths)

        # 4. Prepare Alerts (Side-Channels)
        alerts = []
        if retry_feedback:
            # High-priority feedback from previous attempt
            alerts.append(f"PREVIOUS FAILURE: {retry_feedback}")
            
        # 5. Construct DTO (No context truncation per user request)
        effective_input = current_step.task_query if current_step.task_query else task_input
        
        return StepExecutorInput(
            task_input=effective_input,
            active_folder=active_folder,
            roadmap=self.memory_manager.get_roadmap(),
            session_context=session_context,
            expectations=getattr(current_step, "expected_artifacts", []),
            clipboard=json.dumps(filtered_clipboard, indent=2),
            step_content=current_step.content,
            sop_context=sop_context,
            skill_context=current_step.skill_raw_context or "",
            alerts=alerts
        )

    def _capture_read_results(self, history_messages: List[Any]):
        """
        Scans history for 'read_file' tool outputs and saves them to SessionMemory clipboard.
        This is critical for cross-step context continuity.
        """
        if not history_messages:
            logger.debug("_capture_read_results: No history messages to scan.")
            return
            
        captured_count = 0
        try:
            # We look for pair: 
            # 1. tool_call (msg.role='assistant', msg.tool_calls=[name='read_file', args={path=...}])
            # 2. tool_output (msg.role='tool', tool_call_id=...)
            
            # Simplified Logic: Iterate backwards, find 'tool' messages
            for i, msg in enumerate(reversed(history_messages)):
                if hasattr(msg, "role") and msg.role == "tool":
                    # This message contains the content of a file (presumably)
                    content = getattr(msg, "content", None)
                    tool_call_id = getattr(msg, "tool_call_id", None)
                    
                    if not tool_call_id:
                        logger.debug(f"_capture_read_results: Skipping tool message without tool_call_id.")
                        continue
                    
                    # Find corresponding call to get filename
                    # Look further back
                    found_call = False
                    for j in range(i + 1, len(history_messages)):
                        prev_msg = history_messages[len(history_messages) - 1 - j]
                        if hasattr(prev_msg, "tool_calls") and prev_msg.tool_calls:
                            for tc in prev_msg.tool_calls:
                                tc_id = getattr(tc, "id", None)
                                if tc_id == tool_call_id:
                                    # Found the call
                                    func = getattr(tc, "function", None)
                                    func_name = getattr(func, "name", "") if func else ""
                                    
                                    if "read_file" in func_name or "read_multiple_files" in func_name:
                                        # Parse args to get path
                                        try:
                                            func_args = getattr(func, "arguments", "{}")
                                            args = json.loads(func_args) if isinstance(func_args, str) else func_args
                                            # Handle both single path and array/dict variations if any
                                            paths = []
                                            if "path" in args: paths.append(args["path"])
                                            if "paths" in args: paths.extend(args["paths"])
                                            
                                            # If single outcome, map to single path (heuristic)
                                            if len(paths) == 1 and content:
                                                self.memory_manager.update_clipboard(paths[0], str(content))
                                                logger.info(f"Captured content for '{paths[0]}' to Clipboard ({len(str(content))} chars).")
                                                captured_count += 1
                                            elif len(paths) > 1:
                                                logger.debug(f"_capture_read_results: Multiple paths detected, skipping heuristic capture.")
                                        except Exception as e:
                                            logger.warning(f"Failed to parse read_file args: {e}")
                                    found_call = True
                                    break
                        if found_call: break
            
            if captured_count == 0:
                logger.debug("_capture_read_results: No read_file results captured this cycle.")
                        
        except Exception as e:
            logger.warning(f"Error capturing read results: {e}")
