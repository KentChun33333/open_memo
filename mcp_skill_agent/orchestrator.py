import os
import re
import sys
import json
import asyncio
from typing import Optional, Tuple

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

from config_loader import config
from logger import get_logger, setup_logging
from skill_manager import SkillManager
from sop_agent import SOPAgent, SkillStep
from memory.session_memory import SessionMemoryManager
from step_executor import StepExecutor
from verifier import Verifier
from prompt import PLANNER_INSTRUCTION

# Setup Logger
logger = get_logger("orchestrator")

class Orchestrator:
    """
    The Industrial Orchestrator (Main V3/Pro).
    Manages the lifecycle: Planning -> Discovery -> SOP Execution Loop.
    """
    def __init__(self):
        # 1. Initialize Infrastructure
        setup_logging(level=config.get("logging.level", "INFO"))
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
        
        # 2. Initialize MCP App
        self.app = MCPApp(name="skill_agent_pro", settings=self.config_path)
        
        # 3. Initialize Capabilities
        skills_path = os.path.join(self.base_dir, ".agent", "skills")
        self.skill_manager = SkillManager(skills_dir=skills_path)
        self.memory_manager = SessionMemoryManager(os.getcwd())
        
        logger.info("Orchestrator Initialized.")

    async def run(self, query: str):
        """Main Entry Point."""
        try:
            # --- PHASE 1: PLANNING ---
            skill_name, task_input = await self._run_planning(query)
            if not skill_name:
                logger.error("Planning failed. Aborting.")
                return

            # --- PHASE 2: DISCOVERY & SETUP ---
            tool_context = await self._run_discovery()
            sop = await self._initialize_sop(skill_name)
            
            # --- PHASE 3: EXECUTION LOOP ---
            print("\n========== PHASE 2: EXECUTION (SOP GUIDED) ==========")
            
            while not sop.is_finished():
                current_step = sop.get_current_step()
                if not current_step: break
                
                print(f"\n--- EXECUTION: Step {current_step.id} [{current_step.title}] ---")
                
                # 1. Context Update
                self.memory_manager.update_active_folder()
                
                # 2. Execute Step
                executor = StepExecutor(self.memory_manager, tool_context)
                
                # Retry Loop (Orchestrator Level)
                max_retries = 2
                step_success = False
                retry_feedback = ""
                
                for attempt in range(max_retries + 1):
                    result = await executor.execute(
                        current_step=current_step,
                        task_input=task_input, 
                        skill_name=skill_name,
                        sop_context=sop.get_progress_summary(),
                        retry_feedback=retry_feedback,
                        attempt_idx=attempt
                    )
                    
                    # 3. Verification (The Judge)
                    expectations = getattr(current_step, "expected_artifacts", [])
                    verified, missing, hallucinated = Verifier.verify_artifacts(
                        self.memory_manager.memory.active_folder,
                        result.output,
                        expectations
                    )
                    
                    # 4. Decision Logic
                    # Success conditions:
                    # - Explicit [STEP_COMPLETE] + Verification Pass
                    # - Implicit Success (Expectations Met)
                    # - Script Execution (Optimistic)
                    
                    is_script = "script" in current_step.title.lower() or "run" in current_step.title.lower()
                    explicit_done = "[STEP_COMPLETE]" in result.output
                    
                    if missing and not is_script:
                         logger.warning(f"Validation Failed: Missing {missing}")
                         retry_feedback = f"VALIDATION ERROR: Missing required artifacts: {json.dumps(missing)}"
                    elif hallucinated and not verified and not is_script:
                         logger.warning("Validation Failed: Hallucinated files.")
                         retry_feedback = "VALIDATION ERROR: Files claimed but not found."
                    elif explicit_done or (not missing and expectations) or is_script:
                         # Success!
                         step_success = True
                         
                         # Register Artifacts
                         for vf in verified:
                             self.memory_manager.register_artifact(str(current_step.id), vf)
                         
                         logger.info(f"Step {current_step.id} Complete.")
                         break # Exit Retry Loop
                    else:
                         logger.warning("Step incomplete or verification failed.")
                         retry_feedback = "Step not marked complete or validation failed."
                
                if not step_success:
                    logger.critical(f"Step {current_step.id} Failed after retries.")
                    break
                
                # Advance
                sop.mark_step_done()
                self.memory_manager.save_state()

            print("\n========== MISSION COMPLETE ==========")

        except Exception as e:
            logger.critical(f"Global Error: {e}", exc_info=True)

    # --- Internal Helpers ---

    async def _run_planning(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Determines skill and task input."""
        print("\n========== PHASE 1: PLANNING ==========")
        discovery_info = self.skill_manager.discovery.get_all_skills_info()
        instruction = PLANNER_INSTRUCTION.format(
            available_skills_info=discovery_info,
            query=query
        )
        
        async with self.app.run():
            planner = Agent(name="planner", instruction=instruction, server_names=["skill-server"])
            async with planner:
                llm = await planner.attach_llm(OpenAIAugmentedLLM)
                output = await llm.generate_str(f"Plan for: {query}")
                print(f"[Planner]:\n{output}\n")
                
                skill_match = re.search(r"SKILL_NAME:\s*(.+)", output)
                task_match = re.search(r"SUBAGENT_TASK:\s*(.+)", output, re.DOTALL)
                
                if skill_match and task_match:
                    return skill_match.group(1).strip(), task_match.group(1).strip()
                return None, None

    async def _run_discovery(self) -> str:
        """Lists available tools."""
        agent = Agent(name="discovery", server_names=["skill-server", "file-tools"])
        context = "AVAILABLE TOOLS:\n"
        async with agent:
            res = await agent.list_tools()
            for t in res.tools:
                context += f"- {t.name}: {t.description}\n"
        return context

    async def _initialize_sop(self, skill_name: str) -> SOPAgent:
        """Loads and parses the manual."""
        content = self.skill_manager.get_skill_content(skill_name)
        resources = self.skill_manager.list_skill_contents(skill_name)
        
        sop = SOPAgent(self.app)
        await sop.initialize(content, resources)
        
        # Init Task Artifact
        task_md = "# Task List\n\n"
        for s in sop.steps:
            task_md += f"- [ ] {s.title} <!-- id: {s.id} -->\n"
        with open("task.md", "w") as f: f.write(task_md)
        
        return sop

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <query>")
        sys.exit(1)
        
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(sys.argv[1]))
