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
from ..sop_agent import SkillStep

logger = get_logger("step_executor")

class StepResult:
    def __init__(self, success: bool, output: str, feedback: str = ""):
        self.success = success
        self.output = output
        self.feedback = feedback

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
                      context_switch_warning: str = "") -> StepResult:
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

        # 2. Construct System Prompt (Dynamic)
        subagent_instruction = SUBAGENT_INSTRUCTION.format(
            task_input=task_input,
            active_folder=active_folder,
            roadmap=roadmap,
            session_context=session_context,
            expectations=json.dumps(expectations, indent=2),
            tool_context_str=self.tool_context_str
        )
        
        # Inject Context Switch Warning if present
        if context_switch_warning:
            subagent_instruction += f"\n\n{context_switch_warning}\n"

        # 2b. Defensive Logic: Context Switch Detection
        if retry_feedback:
            subagent_instruction += f"\n\n[PREVIOUS FAILURE]: {retry_feedback}\n"
        
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

        final_response = ""
        
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            
            # Initial User Prompt
            user_prompt = USER_PROMPT_TEMPLATE.format(
                step_id=current_step.id,
                step_title=current_step.title,
                step_content=current_step.content,
                sop_context=sop_context
            )
            
            # 4. ReAct Loop (Semi-Autonomous with Interventions)
            # We use a finite loop to prevent runaway agents
            react_max_cycles = 10 
            cycle = 0
            
            while cycle < react_max_cycles:
                cycle += 1
                
                # Dynamic Prompting Strategy
                # Cycle 1: The actual task.
                # Cycle 2+: "Continue/Update" if not done.
                current_prompt = user_prompt if cycle == 1 else "Status Update: Continue execution. If done, output [STEP_COMPLETE]."
                
                try:
                    # The Agent's internal generate_loop handles tool calls (up to 15 iterations)
                    response = await llm.generate_str(current_prompt, RequestParams(max_iterations=self.max_react_steps))
                    final_response = response
                    
                    final_response = response
                    
                    logger.debug(f"[{worker_name}] Cycle {cycle} Output: {response[:100]}...")
                    if self.telemetry:
                        self.telemetry.log_event(
                            event_type="ACTION", 
                            step_id=current_step.id,
                            agent_name=worker_name,
                            details={"cycle": cycle, "response_preview": response[:200]}
                        )

                    # --- Intervention: Auto-Write ---
                    if "```" in response and "write_file" not in response:
                        logger.info("Intervention: Triggering Auto-Write for code blocks.")
                        await llm.generate_str(AUTO_WRITE_PROMPT, RequestParams(max_iterations=10))
                    
                    # --- Check for Completion Signal ---
                    if "[STEP_COMPLETE]" in response:
                        break
                        
                except Exception as e:
                    logger.error(f"[{worker_name}] Error in Cycle {cycle}: {e}")
                    final_response += f"\nError: {e}"
                    break
        
        # 5. Return Result (No verification here - Caller does that)
        return StepResult(
            success=True, # Tentative, Verify decides
            output=final_response
        )

