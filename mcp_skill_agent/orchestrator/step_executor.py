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
from ..prompt import SUBAGENT_INSTRUCTION, USER_PROMPT_TEMPLATE, AUTO_WRITE_PROMPT
from ..prompt import SUBAGENT_INSTRUCTION, USER_PROMPT_TEMPLATE, AUTO_WRITE_PROMPT
from .structs import WorkerHandover, StepHandover, SkillStep # Explicit import

# Initialize Logger
logger = get_logger("step_executor")

class StepExecutor:
    """
    Controller Component: Step Execution Manager.
    - Manages the lifecycle of a single SOP step.
    - Spawns an EPHEMERAL Worker Agent.
    - Runs the ReAct loop.
    """
    def __init__(self, memory_manager: SessionMemoryManager, tool_context_str: str, telemetry: Any = None):
        self.memory_manager = memory_manager
        self.tool_context_str = tool_context_str
        self.telemetry = telemetry
        self.max_react_steps = 15 # Configurable?

    async def execute(self, 
                      current_step: SkillStep, 
                      task_input: str, 
                      skill_name: str, 
                      sop_context: str,
                      retry_feedback: str = "",
                      attempt_idx: int = 0,
                      context_switch_warning: str = "") -> StepHandover:
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
        roadmap = self.memory_manager.get_roadmap()
        expectations = getattr(current_step, "expected_artifacts", [])

        # 2. Build Handover Envelope (Protocol Layer)
        # Use specific task_query if available, else fallback to global task_input
        effective_input = current_step.task_query if current_step.task_query else task_input
        
        handover = WorkerHandover(
            task_input=effective_input,
            active_folder=active_folder,
            roadmap=roadmap,
            session_context=session_context,
            tool_definitions=self.tool_context_str,
            expectations=expectations
        )
        
        # 2b. Inject Warnings (Side-channel)
        if context_switch_warning:
            handover.task_input += f"\n\n[WARNING]: {context_switch_warning}"
        if retry_feedback:
            handover.task_input += f"\n\n[PREVIOUS FAILURE]: {retry_feedback}"

        # 3. Construct System Prompt (Dynamic)
        subagent_instruction = SUBAGENT_INSTRUCTION.format(
            worker_context_xml=handover.to_xml()
        )
        
        # Log Start
        self.memory_manager.log_event(f"Step {current_step.id} Started: {current_step.title}")
        if self.telemetry:
            self.telemetry.log_event(
                event_type="STEP_START",
                step_id=current_step.id,
                details={"title": current_step.title, "attempt": attempt_idx}
            )

        # 3. Spawn Ephemeral Agent
        worker_name = f"Worker-{skill_name}-{current_step.id}-{attempt_idx}"
        worker = Agent(
            name=worker_name,
            instruction=subagent_instruction,
            server_names=["skill-server", "file-tools"] 
        )

        logger.info(f"Spawning Worker: {worker_name} in {active_folder}")
        logger.debug(f"Tool Context for Worker: {self.tool_context_str[:200]}...")


        final_response = ""
        success_signal = False
        
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            
            # Initial User Prompt
            # Prepend generated task_instruction to content
            combined_content = current_step.content
            if current_step.task_instruction:
                combined_content = f"**STRATEGIC PLAN**: {current_step.task_instruction}\n\n**REFERENCE MANUAL**:\n{current_step.content}"

            user_prompt = USER_PROMPT_TEMPLATE.format(
                step_id=current_step.id,
                step_title=current_step.title,
                step_content=combined_content,
                sop_context=sop_context
            )
            
            # 4. ReAct Loop (Smart Loop)
            # We use a finite loop to prevent runaway agents
            react_max_cycles = 10 
            cycle = 0
            
            # Track tool usage (heuristic)
            tool_usage_history = []
            
            # Heuristic: Is this a coding step?
            is_coding_step = any(kw in current_step.title.lower() for kw in ['code', 'implement', 'write', 'create'])
            
            while cycle < react_max_cycles:
                cycle += 1
                
                # Dynamic Prompting Strategy
                if cycle == 1:
                     current_prompt = user_prompt
                else:
                    # Smart Analysis of Previous Turn
                    last_action_tools = tool_usage_history[-1] if tool_usage_history else []
                    has_written = any(t in last_action_tools for t in ['write_file', 'write_files'])
                    
                    if is_coding_step and not has_written and success_signal:
                        current_prompt = "REJECTION: You submitted success but no code was written. Write the file."
                    else:
                        current_prompt = "Status Update: Continue execution. If done, output JSON."
                
                try:
                    # The Agent's internal generate_loop handles tool calls (up to 15 iterations)
                    response = await llm.generate_str(current_prompt, RequestParams(max_iterations=self.max_react_steps))
                    final_response = response
                    
                    logger.debug(f"[{worker_name}] Cycle {cycle} Output: {response[:100]}...")
                    
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
                                break # Exit Loop
                        except json.JSONDecodeError:
                            logger.warning(f"[{worker_name}] Invalid JSON Detected.")
                            
                    # --- Intervention: Auto-Write (The "Catch-All") ---
                    if "```" in response and "write_file" not in response and not success_signal:
                        # Simple Auto-Write trigger if needed, or pass
                        pass
                        
                except Exception as e:
                    logger.error(f"[{worker_name}] Error in Cycle {cycle}: {e}")
                    final_response += f"\nError: {e}"
                    break
        
        # 5. Return Result
        return StepHandover(
            success=True, # Tentative, Verify decides
            output=final_response
        )
