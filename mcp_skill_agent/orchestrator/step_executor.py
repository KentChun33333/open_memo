import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams

from ..logger import get_logger
from ..config_loader import config
from ..memory.session_memory import SessionMemoryManager
from ..prompt import INSTRUCTION_POOL, SUBAGENT_INSTRUCTION, USER_PROMPT_TEMPLATE, AUTO_WRITE_PROMPT, GENERAL_SKILL_PROTOCOL
from .structs import StepExecutorInput, StepExecutorOutput, SkillStep, TechLeadInput # Explicit import
from .structs import StepExecutorInput, StepExecutorOutput, SkillStep, TechLeadInput # Explicit import

# Initialize Logger
logger = get_logger("step_executor")

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
        self.max_react_steps = 15 # Configurable?

    async def execute(self, 
                      current_step: SkillStep, 
                      task_input: str, 
                      skill_name: str, 
                      # sop_context removed
                      retry_feedback: str = "",
                      attempt_idx: int = 0,
                      context_switch_warning: str = "") -> StepExecutorOutput:
        """
        Executes a single attempt of a step.
        """
        # 1. Prepare Context (Snapshot)
        active_folder = self.memory_manager.memory.active_folder
        session_snapshot = {
            "artifacts": self.memory_manager.memory.artifacts,
            "env_vars": self.memory_manager.memory.env_vars
        }
        session_context = json.dumps(session_snapshot, indent=2)
        expectations = getattr(current_step, "expected_artifacts", [])

        # 1b. Self-Generate SOP Context from Memory
        sop_context = "Task List:\n"
        plan = self.memory_manager.get_plan()
        
        if not plan:
             sop_context += "(No Plan Found in Memory)\n"
        else:
             for s in plan:
                 # Dictionary access because plan is List[Dict]
                 s_id = s.get("id")
                 s_title = s.get("title")
                 s_status = s.get("status")
                 
                 mark = "[ ]"
                 if s_id < current_step.id: mark = "[x]"
                 elif s_id == current_step.id: mark = "[/]"
                 elif s_status == "done": mark = "[x]"
                 
                 sop_context += f"{mark} {s_title}\n"

        # 2. Build Handover Envelope (Protocol Layer)
        # Use specific task_query if available, else fallback to global task_input
        effective_input = current_step.task_query if current_step.task_query else task_input
        
        # --- Context Optimization: Recent Access Policy ---
        # Only inject files accessed in the last 2 steps
        recent_paths = self.memory_manager.get_recent_file_paths(lookback_steps=2)
        filtered_clipboard = self.memory_manager.get_clipboard_subset(recent_paths)
        
        handover = StepExecutorInput(
            task_input=effective_input,
            active_folder=active_folder,
            roadmap=self.memory_manager.get_roadmap(),

            session_context=session_context,
            expectations=expectations,
            clipboard=json.dumps(filtered_clipboard, indent=2), # Inject Filtered File Cache
            step_content=current_step.content, # New: Full instruction in System Prompt
            sop_context=sop_context,           # New: Full SOP Context in System Prompt
            skill_context=current_step.skill_raw_context # New: Inject SKILL.md
        )
        
        # 2b. Inject Warnings (Side-channel)
        if retry_feedback:
            handover.task_input += f"\n\n[PREVIOUS FAILURE]: {retry_feedback}"

        # 3. Construct System Prompt (Dynamic Persona)
        
        # Default Persona
        current_persona = "DEFAULT"
        base_instruction = INSTRUCTION_POOL["DEFAULT"]
        subagent_instruction = base_instruction.format(
            worker_context_xml=handover.to_xml(),
            general_skill_protocol=GENERAL_SKILL_PROTOCOL
        )
        
        # Log Start
        self.memory_manager.log_event(f"Step {current_step.id} Started: {current_step.title}")
        if self.telemetry:
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

        logger.info(f"Spawning Worker: {worker_name} in {active_folder}")



        final_response = ""
        success_signal = False
        
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            
            # Initial User Prompt (Simplified Trigger)
            # The heavy lifting is now in the System Prompt (handover.to_xml())
            user_prompt = f"ACTION: Execute Step {current_step.id}: {current_step.title}. Refer to <StepContent> for details."
            
            # 4. ReAct Loop (Smart Loop)
            react_max_cycles = 15 
            cycle = 0
            
            # Track tool usage (heuristic)
            # tool_usage_history = [] # REMOVED: Managed by SessionMemory
            
            # Heuristic: Is this a coding step?
            is_coding_step = any(kw in current_step.title.lower() for kw in ['code', 'implement', 'write', 'create'])
            
            while cycle < react_max_cycles:
                cycle += 1
                
                # Fetch Tool History from Memory
                current_tool_history = self.memory_manager.get_tool_history(current_step.id)

                if cycle == 1:
                    current_prompt = user_prompt
                else:
                    # Simple Continuation Prompt
                    current_prompt = "Status Update: Continue execution. If done, output JSON."

                try:
                    # The Agent's internal generate_loop handles tool calls (up to 15 iterations)
                    response = await llm.generate_str(current_prompt, RequestParams(max_iterations=self.max_react_steps))
                    final_response = response
                    
                    # --- Capture Tool Usage for Router ---
                    # We inspect the agent's recent history to find tool calls
                    current_cycle_tools = [] # List of (name, args)
                    try:
                        # Inspect recent messages in worker history
                        # Assuming worker.history or llm.history is a list of messages
                        history_source = getattr(worker, "history", []) or getattr(llm, "history", [])
                        if hasattr(history_source, "messages"): 
                             history_source = history_source.messages
                        
                        if not isinstance(history_source, list):
                             # Log type for debugging but default to empty to allow flow to continue
                             logger.debug(f"History source is not a list: {type(history_source)}")
                             history_source = []
                        
                        # Look at the last few messages (since we just ran generate_str)
                        # We are looking for messages with 'tool_calls' or similar
                        for msg in history_source[-15:]: 
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

    def _capture_read_results(self, history_messages: List[Any]):
        """
        Scans history for 'read_file' tool outputs and saves them to SessionMemory clipboard.
        """
        try:
            # We look for pair: 
            # 1. tool_call (msg.role='assistant', msg.tool_calls=[name='read_file', args={path=...}])
            # 2. tool_output (msg.role='tool', tool_call_id=...)
            
            # Simplified Logic: Iterate backwards, find 'tool' messages
            for i, msg in enumerate(reversed(history_messages)):
                if hasattr(msg, "role") and msg.role == "tool":
                    # This message contains the content of a file (presumably)
                    content = msg.content
                    tool_call_id = msg.tool_call_id
                    
                    # Find corresponding call to get filename
                    # Look further back
                    found_call = False
                    for j in range(i + 1, len(history_messages)):
                        prev_msg = history_messages[len(history_messages) - 1 - j]
                        if hasattr(prev_msg, "tool_calls") and prev_msg.tool_calls:
                            for tc in prev_msg.tool_calls:
                                if tc.id == tool_call_id:
                                    # Found the call
                                    if "read_file" in tc.function.name or "read_multiple_files" in tc.function.name:
                                        # Parse args to get path
                                        try:
                                            args = json.loads(tc.function.arguments)
                                            # Handle both single path and array/dict variations if any
                                            paths = []
                                            if "path" in args: paths.append(args["path"])
                                            if "paths" in args: paths.extend(args["paths"])
                                            
                                            # If single outcome, map to single path (heuristic)
                                            if len(paths) == 1:
                                                  self.memory_manager.update_clipboard(paths[0], str(content))
                                                  # logger.info(f"Captured content for {paths[0]} to Clipboard.")
                                        except Exception as e:
                                            logger.warning(f"Failed to parse read_file args: {e}")
                                    found_call = True
                                    break
                        if found_call: break
        except Exception as e:
            logger.warning(f"Error capturing read results: {e}")
