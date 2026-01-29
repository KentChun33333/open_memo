import asyncio
import os
import re
import sys
import glob
import json
import logging
from typing import List, Dict, Any, Optional

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from skill_manager import SkillManager
from navigator import Navigator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stderr
)
# Reduce noise
logging.getLogger("mcp_agent").setLevel(logging.WARNING) 
logger = logging.getLogger("main_v3")

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")



# --- AGENT PROMPTS ---

MANAGER_INSTRUCTION = """You are the MANAGER.
Your goal is to break down the User's Request into a sequence of ATOMIC STEPS.
You have access to a library of Skills.

User Request: "{query}"

Available Skills:
{available_skills}

INSTRUCTIONS:
1. Select the most relevant skill (if any).
2. Decompose the request into a list of steps.
3. For EACH step, you MUST define a "Verification Artifact" - a file that checks if the step is done.
4. IMPORTANT: Keep paths SIMPLE. Do not create deep nested structures like 'projects/my-app' unless explicitly asked. Prefer 'my-app/'.

OUTPUT JSON FORMAT ONLY:
{{
  "skill_used": "skill_name_or_none",
  "steps": [
    {{
      "title": "Short Title",
      "goal": "Precise instruction. Mention `mkdir -p` if creating directories.",
      "artifact": "verification/file.ext" 
    }}
  ]
}}
"""

WORKER_VP_PROMPT = """You are a WORKER Agent.
Your Goal: {goal}
Current Working Directory: {active_dir}

ROADMAP (Overview):
{roadmap}

INSTRUCTIONS:
1. Execute the task using available tools.
2. If you create a file, ENSURE it is written to disk.
3. IMPORTANT: `run_command` does not persist directory state. Always chain your commands:
   `cd {active_dir} && <your_command>`
4. When finished, output: [STEP_COMPLETE]
"""

DEVELOPMENT_PROMPT = """You are now in the DEVELOPMENT phase.
Your goal: Implement the application logic.

GOAL: {goal}
ACTIVE_DIR: {active_dir}

### INSTRUCTIONS
1. **Explore**: Use `ls -R` to find the directory structure.
2. **Plan**: Identify which files need modification.
3. **Execute**: For every file you create or modify, you MUST follow this format:
   
   FILE: <path_relative_to_project_root>
   ```language
   // code here
   ```

4. **Persist**: Use the `write_file` tool for every file identified above.
5. **Verify**: Use `ls -R` after writing to confirm the files are on disk.

CONTEXT
CONTEXT
ACTIVE_DIR: {active_dir}

ROADMAP (Overview):
{roadmap}

IMPORTANT:
- `run_command` usage: ALWAYS chain `cd {active_dir} && command`.
- Do not use purple gradients or 'AI slop' designs. Focus on clean, professional implementation.
- When done and verified, output [STEP_COMPLETE].
"""

class Orchestrator:
    def __init__(self):
        self.app = MCPApp(name="Industrial_Orchestrator_v3", settings=config_path)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skills_path = os.path.join(base_dir, ".agent", "skills")
        self.skill_manager = SkillManager(skills_dir=skills_path)
        self.context = {
            "workspace_root": os.getcwd(),
            "active_dir": os.getcwd() # Dynamic
        }
        self.navigator = Navigator(self.context["workspace_root"])

    async def run_manager(self, query: str) -> Dict[str, Any]:
        """Runs the Manager Agent to produce the Plan."""
        skills_info = self.skill_manager.discovery.get_all_skills_info()
        
        instruction = MANAGER_INSTRUCTION.format(
            query=query,
            available_skills=skills_info
        )
        
        print("\n========== PHASE 1: MANAGER PLANNING ==========")
        async with self.app.run():
            manager = Agent(
                name="Manager",
                instruction=instruction,
                server_names=["skill-server"]
            )
            async with manager:
                llm = await manager.attach_llm(OpenAIAugmentedLLM)
                # Max iterations=1 because we just want the plan, no tool usage really needed unless it wants to read skill details
                # But to be safe, maybe allow it to read skills.
                response = await llm.generate_str("Create the Execution Plan.", RequestParams(max_iterations=5))
                
                # Extract JSON
                try:
                    # Naive extraction - improved industrial version would use a parser utility
                    json_str = response.strip()
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0]
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0]
                    
                    plan = json.loads(json_str)
                    print(f"[Manager] Plan Created: {len(plan.get('steps', []))} steps.")
                    return plan
                except Exception as e:
                    logger.error(f"Failed to parse Manager plan: {e}")
                    print(f"[Manager Raw Output]: {response}")
                    return None

    async def execute_step(self, step: Dict[str, str], retry_count: int = 0):
        """Executes a single step with a fresh Worker."""
        print(f"\n>>> EXECUTING STEP: {step['title']}")
        print(f"    GOAL: {step['goal']}")
        print(f"    TARGET ARTIFACT: {step['artifact']}")
        print(f"    CWD: {self.context['active_dir']}")

        # Select Prompt based on Step Type
        is_coding_step = any(kw in step['title'].lower() for kw in ["develop", "code", "implement", "react", "app"])
        is_coding_step = is_coding_step or any(kw in step['goal'].lower() for kw in ["write", "create file", "component"])
        
        roadmap = self.navigator.get_roadmap(self.context['active_dir'])

        if is_coding_step:
            print("    [System] Detected Development Step. Using Coding Protocol.")
            worker_instruction = DEVELOPMENT_PROMPT.format(
                goal=step['goal'],
                active_dir=self.context['active_dir'],
                roadmap=roadmap
            )
        else:
            worker_instruction = WORKER_VP_PROMPT.format(
                goal=step['goal'],
                active_dir=self.context['active_dir'],
                roadmap=roadmap
            )
        
        # Fresh Worker for every step (Industrial Pattern: Stateless Execution)
        worker = Agent(
            name=f"Worker-{step['title']}-{retry_count}",
            instruction=worker_instruction,
            server_names=["skill-server", "file-tools"]
        )
        
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            try:
                # We use generate_str with high iterations for ReAct self-correction within the step
                response = await llm.generate_str(
                    f"Execute Step: {step['title']}", 
                    RequestParams(max_iterations=15) # Increased for coding
                )
                
                # --- INTERVENTION: Smarter Auto-Write (DeepCode Pattern) ---
                if "FILE:" in response and "write_file" not in response:
                     print("    [System] 'FILE:' claim detected but tool execution unclear. Checking...")
                     
                     # Extract matches: FILE: <path>
                     missed_files = re.findall(r"FILE:\s*([^\s\n]+)", response)
                     
                     if missed_files:
                         print(f"    [System] Detected missed writes for: {missed_files}. Triggering Intervention.")
                         aw_prompt = f"""You identified '{missed_files}' but didn't call the tool.
                         Call `write_file` for EACH of these paths NOW with the code you provided.
                         Then output [STEP_COMPLETE]."""
                         
                         await llm.generate_str(
                             aw_prompt,
                             RequestParams(max_iterations=10)
                         )

                return response
            except Exception as e:
                logger.error(f"Worker failed: {e}")
                return str(e)

    async def run(self, query: str):
        # 1. Manager Phase
        plan = await self.run_manager(query)
        if not plan or not plan.get("steps"):
            print("Error: No valid plan generated.")
            return

        steps = plan["steps"]
        
        # 2. Execution Loop
        print("\n========== PHASE 2: WORKER EXECUTION ==========")
        async with self.app.run(): # Re-enter app context for workers
             for step in steps:
                 step_success = False
                 
                 # Retry Loop
                 for attempt in range(3):
                     # A. Dynamic Path Finding (The Path Finder)
                     self.context["active_dir"] = self.navigator.find_project_root(self.context["workspace_root"])
                     
                     # B. Run Worker
                     await self.execute_step(step, attempt)
                     
                     # C. Reality Check (Disk verification)
                     # Resolve expected artifact path relative to ACTIVE dir
                     check_path = os.path.join(self.context["active_dir"], step["artifact"])
                     
                     if os.path.exists(check_path):
                         print(f"✓ VERIFIED: {step['artifact']} exists.")
                         step_success = True
                         break
                     else:
                         print(f"✗ FAILED: {step['artifact']} not found at {check_path}.")
                         print("  Retrying...")
                 
                 if not step_success:
                     print(f"!!! CRITICAL FAILURE: Step '{step['title']}' could not be verified after 3 attempts.")
                     break
                     
        print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = 'please build a web artifact that example the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(query))
