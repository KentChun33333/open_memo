import os
import re
import sys
import json
import asyncio
from typing import Optional, Tuple, List, Dict, Union

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

from ..config_loader import config
from ..logger import get_logger, setup_logging
from ..memory.session_memory import SessionMemoryManager
from .step_executor import StepExecutor
from .structs import SkillStep, CriticInput, CriticOutput, AtomicPlannerInput, AtomicPlannerOutput # Explicit import
from ..prompt import PLANNER_INSTRUCTION
from ..telemetry import TelemetryManager

# Setup Logger
logger = get_logger("orchestrator")
from ..skill_manager import SkillManager
from .atomic_planner import AtomicPlanner
from .verifier import Verifier


class Orchestrator:
    """
    The Industrial Orchestrator (Main V3/Pro).
    Manages the lifecycle: Planning -> Discovery -> SOP Execution Loop.
    """
    def __init__(self):
        # 1. Initialize Infrastructure
        setup_logging(level=config.get("logging.level", "INFO"))
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Config path: mcp_skill_agent/config.yaml
        config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # mcp_skill_agent
        self.config_path = os.path.join(config_dir, "config.yaml")
        
        # 2. Initialize MCP App
        self.app = MCPApp(name="skill_agent_pro", settings=self.config_path)
        
        # 3. Initialize Capabilities
        skills_path = os.path.join(self.base_dir, ".agent", "skills")
        self.skill_manager = SkillManager(skills_dir=skills_path)
        self.memory_manager = SessionMemoryManager(os.getcwd())
        self.telemetry = TelemetryManager()
        self.verifier = Verifier(self.memory_manager)
        
        logger.info("Orchestrator Initialized.")

    async def run(self, query: str):
        """Main Entry Point."""
        task_input = query # Alias for consistency
        try:
            async with self.app.run():
                # --- PHASE 1: ATOMIC PLANNING ---
                skill_name = await self._discover_skill(query)
                if not skill_name:
                    logger.error("Planning failed. Aborting.")
                    return

                skill_context = await self._discover_skill_context(skill_name)
                plan_output = await self._plan_atomic_steps(skill_context, query)
                steps = self._enforce_required_scripts(
                    steps=plan_output.steps,
                    required_scripts=self.skill_manager.get_required_scripts(skill_name)
                )
                
                
                # --- PHASE 2: EXECUTION LOOP ---
                tool_context = skill_context.tool_definitions
                print("\n========== PHASE 2: EXECUTION (SOP GUIDED) ==========")
                
                step_idx = 0
                sop = AtomicPlanner() # Helper for replanning

                while step_idx < len(steps):
                    current_step = steps[step_idx]
                    current_step.status = "active"
                    print(f"\n--- EXECUTION: Step {current_step.id} [{current_step.title}] ---")
                    
                    # Persist plan and step context
                    self.memory_manager.save_plan(steps)
                    self.memory_manager.memory.current_step_id = current_step.id
                    self.memory_manager.save_state()
                    
                    # 2. Execute Step (LLM)
                    # Note: We rely on the LLM (StepExecutor) to decide whether to run a script 
                    # via the 'skill-server' tool or perform other actions.
                    
                    executor = StepExecutor(self.memory_manager, tool_context, self.telemetry)
                    
                    # Retry Loop (Orchestrator Level)
                    max_retries = 2
                    step_success = False
                    retry_feedback = ""
                    
                    # Update status in memory
                    self.memory_manager.update_step_status(current_step.id, "running")
                    
                    for attempt in range(max_retries + 1):
                        result = await executor.execute(
                            current_step=current_step,
                            task_input=task_input, 
                            skill_name=skill_name,
                            # sop_context removed (Self-Service)
                            retry_feedback=retry_feedback,
                            attempt_idx=attempt
                        )
                        
                        # 3. Verification (The Judge)
                        expectations = getattr(current_step, "expected_artifacts", [])
                        verified, missing, hallucinated = self.verifier.verify_artifacts(
                            result.output,
                            expectations
                        )
                        
                        # 4. Decision Logic
                        explicit_done = "[STEP_COMPLETE]" in result.output
                        
                        if missing:
                             logger.warning(f"Validation Failed: Missing {missing}")
                             retry_feedback = f"VALIDATION ERROR: Missing required artifacts: {json.dumps(missing)}"
                        elif hallucinated and not verified:
                             logger.warning("Validation Failed: Hallucinated files.")
                             retry_feedback = "VALIDATION ERROR: Files claimed but not found."
                        elif explicit_done or (not missing and expectations):
                             # Success!
                             
                             # --- CRITIC PHASE ---
                             global_ctx = skill_context.raw_content
                             critic_result = await self._run_critic_phase(result.output, current_step, global_context=global_ctx)
                             
                             if critic_result.decision == "APPROVED":
                                 step_success = True
                                 
                                 # Register Artifacts
                                 for vf in verified:
                                     self.memory_manager.register_artifact(str(current_step.id), vf)
                                 
                                 logger.info(f"Step {current_step.id} Complete (Approved by Critic).")
                                 
                                 # Attempt to detect path shifts after successful step
                                 # This handles cases where 'init' script was run by LLM
                                 self._try_update_active_folder()
                                 
                                 break # Exit Retry Loop
                             else:
                                 # Critic Rejected
                                 logger.warning(f"Critic Rejected Step {current_step.id}")
                                 retry_feedback = f"CRITIC REJECTED your work. Feedback:\n{critic_result.feedback}\nFIX THESE ISSUES IMMEDIATELY."
                                 # Continue to next attempt
                        else:
                             logger.warning("Step incomplete or verification failed.")
                             retry_feedback = "Step not marked complete or validation failed."
                    
                    if not step_success:
                        logger.warning(f"Step {current_step.id} Failed after retries.")
                        
                        # === DYNAMIC SELF-HEALING ===
                        logger.info(f"Initiating Self-Healing for Step {current_step.id}...")
                        new_plan = await sop.replan(
                            current_plan=AtomicPlannerOutput(steps=steps),
                            failed_step=current_step,
                            failure_reason=retry_feedback,
                            skill_content=skill_context.raw_content
                        )
                        
                        if new_plan.steps:
                            logger.info("Self-Healing Successful. Injecting new steps.")
                            # Replace failed step and ALL subsequent steps with the recovery plan
                            # The recovery plan is expected to cover the rest of the mission
                            steps = steps[:step_idx] + new_plan.steps
                            # Do NOT increment step_idx, because we want to execute the first step of the new plan immediately
                            continue 
                        else:
                            logger.critical("Self-Healing Failed. Aborting Mission.")
                            break

                    # Advance
                    current_step.status = "done"
                    self.memory_manager.save_state()
                    step_idx += 1

                print("\n========== MISSION COMPLETE ==========")

        except Exception as e:
            logger.critical(f"Global Error: {e}", exc_info=True)

    # --- Internal Helpers ---
    
    def _try_update_active_folder(self):
        """
        Heuristic: Check if a new directory appeared and switch to it if appropriate.
        Prevents recursive nesting by checking real paths.
        """
        new_root = self._find_newest_dir(self.memory_manager.memory.active_folder)
        if new_root and new_root != self.memory_manager.memory.active_folder:
            # Prevent switching to a parent directory or staying same
            if new_root.startswith(self.memory_manager.memory.active_folder):
                 logger.info(f"Switching active folder to {new_root}")
                 self.memory_manager.update_active_folder(new_root)

    async def _run_critic_phase(self, worker_output: str, current_step: SkillStep, global_context: str = "") -> CriticOutput:
        """
        Generalized Critic Phase.
        Technical Audit with Structured Handover and Telemetry.
        """
        # 1. Detect if this is a technical step
        keywords = ["develop", "code", "build", "script", "implement", "create"]
        needs_technical_audit = any(kw in current_step.title.lower() for kw in keywords)

        if not needs_technical_audit:
            return CriticOutput(decision="APPROVED", feedback="(Non-technical step)")
            
        # 2. Prepare Structured Context
        from .structs import CriticInput
        from ..prompt import CRITIC_INSTRUCTION
        
        roadmap = self.memory_manager.get_roadmap()
        expectations = getattr(current_step, "expected_artifacts", [])
        
        # Use CriticInput DTO
        handover = CriticInput(
            step_id=current_step.id,
            step_title=current_step.title,
            worker_output=worker_output,
            active_folder=self.memory_manager.memory.active_folder,
            roadmap=roadmap,
            global_context=global_context, # Pass global context
            expectations=expectations
        )
        
        critic_xml_context = handover.to_xml()
        
        # 3. Telemetry: Start
        self.telemetry.log_event(
            event_type="CRITIC_START",
            step_id=current_step.id,
            agent_name="Technical-Critic",
            details={"step_title": current_step.title}
        )

        logger.info(f"[Orchestrator] Invoking Technical Critic for '{current_step.title}'...")

        # 4. Construct Instruction
        instruction = CRITIC_INSTRUCTION.format(
            context_xml=critic_xml_context
        )

        critic = Agent(name="Technical-Critic", instruction=instruction, server_names=["file-tools", "skill-server"])
        
        async with critic:
            llm_critic = await critic.attach_llm(OpenAIAugmentedLLM)
            # Short prompt since context is in system instruction
            critic_prompt = "Perform the audit based on the provided XML Context. Output [APPROVED] or [REJECTED] with feedback."
            
            critic_response = await llm_critic.generate_str(critic_prompt)
            
            # 5. Telemetry: Decision
            decision = "APPROVED" if "[APPROVED]" in critic_response else "REJECTED"
            
            # Log to Blackboard (Persistent Memory)
            self.memory_manager.log_agent_feedback(
                step_id=current_step.id,
                agent_name="Technical-Critic",
                feedback=critic_response,
                feedback_type=decision
            )

            self.telemetry.log_event(
                event_type="CRITIC_DECISION",
                step_id=current_step.id,
                agent_name="Technical-Critic",
                details={"decision": decision, "feedback_snippet": critic_response[:100]}
            )
            
            print(f"[Critic Feedback]:\n{critic_response}\n")
            return CriticOutput(decision=decision, feedback=critic_response)

    async def _discover_skill(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Determines skill and task input."""
        print("\n========== PHASE 1: PLANNING ==========")
        discovery_info = self.skill_manager.discovery.get_all_skills_info()
        instruction = PLANNER_INSTRUCTION.format(
            available_skills_info=discovery_info,
            query=query
        )
        skii_man = Agent(name="skill_discovery", instruction=instruction, server_names=["skill-server"])
        async with skii_man:
            llm = await skii_man.attach_llm(OpenAIAugmentedLLM)
            output = await llm.generate_str(f"Check for: {query}")
            print(f"[Check]:\n{output}\n")
            
            skill_match = re.search(r"SKILL_NAME:\s*(.+)", output)
            
            if skill_match:
                # Pass the original query as the task input
                return skill_match.group(1).strip()
            return None

    async def _discover_skill_context(self, skill_name: str) -> 'SkillContextDTO':
        """
        Phase 1: Context Discovery (The Librarian).
        Fetches all skill resources up front.
        """
        from .structs import SkillContextDTO
        
        logger.info(f"Discovering context for skill: {skill_name}")
        
        # 1. Load Content
        raw_content = self.skill_manager.get_skill_content(skill_name)
        references = self.skill_manager.list_skill_contents(skill_name)
        
        # 2. Get Tools
        # Note: Ideally we filter tools by skill, but for now we get all available tools
        # or we could ask discovery agent to filter.
        # Keeping it simple: get all tools for now, as in original _run_discovery
        tool_context = await self._run_discovery() 
        
        # 3. Get Internal Roadmap (if any)
        # We can scan the skill directory itself
        skill_path = os.path.join(self.skill_manager.skills_dir, skill_name)
        roadmap = ""
        return SkillContextDTO(
            skill_name=skill_name,
            raw_content=raw_content,
            references=references,
            roadmap=roadmap,
            tool_definitions=tool_context
        )

    async def _run_discovery(self) -> str:
        """Lists available tools."""
        agent = Agent(name="discovery", server_names=["skill-server", "file-tools"])
        context = "AVAILABLE TOOLS:\n"
        async with agent:
            try:
                res = await agent.list_tools()
                for t in res.tools:
                    context += f"- {t.name}: {t.description}\n"
            except Exception as e:
                logger.error(f"Discovery failed: {e}")
                context += "(Tool discovery failed)"
        return context

    async def _plan_atomic_steps(self, skill_context: 'SkillContextDTO', task_input: str) -> AtomicPlannerOutput:
        """
        Phase 2: Atomic Step Planning (The Architect).
        Maps Protocol Constraints (from SkillContext) + User Intent (task_input) -> Atomic Actions.
        """
        logger.info(f"Planning atomic steps for task: {task_input[:50]}...")
        
        sop = AtomicPlanner()
        
        # Inject DTO context into SOP for the planner prompt
        # Use AtomicPlannerInput DTO
        input_data = AtomicPlannerInput(
            query=task_input,
            skill_content=skill_context.raw_content,
            resources="\n".join(skill_context.references) if isinstance(skill_context.references, list) else str(skill_context.references)
        )
        
        # Store raw content for later injection (legacy, might be redundant with SkillContextDTO but safer to keep)
        # We don't need to store sop.raw_content anymore as sop is stateless
        # We might need to pass it to Critic later, but Orchestrator has skill_context
        
        plan_output = await sop.plan(input_data)
        
        return plan_output

    def _find_newest_dir(self, base_dir: str) -> Optional[str]:
        try:
            entries = []
            for name in os.listdir(base_dir):
                path = os.path.join(base_dir, name)
                if not os.path.isdir(path):
                    continue
                if name.startswith(".") or name in {".git", "node_modules", "__pycache__", ".agent"}:
                    continue
                entries.append(path)
            if not entries:
                return None
            entries.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            
            # Check duplication - if newest dir name == current dir name, it might be recursive
            # But here base_dir IS current dir.
            # We just return the path. Logic elsewhere handles checks.
            return entries[0]
            
        except Exception as e:
            logger.warning(f"Failed to detect newest dir: {e}")
            return None
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <query>")
        sys.exit(1)
        
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(sys.argv[1]))
