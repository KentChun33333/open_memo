import asyncio
import os
import re
import sys
import json
import logging
from typing import List, Dict, Any, Optional

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from skill_manager import SkillManager
from memory.session_memory import SessionMemory
from validator import Validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stderr
)
logging.getLogger("mcp_agent").setLevel(logging.WARNING)
logger = logging.getLogger("orchestrator_v3")

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# --- PROMPTS ---

MANAGER_INSTRUCTION = """You are the MANAGER.
Your goal is to break down the User's Request into a sequence of ATOMIC STEPS.

User Request: "{query}"

Available Skills:
{available_skills}

INSTRUCTIONS:
1. Select the most relevant skill (if any).
2. Decompose the request into steps.
3. For EACH step, define a "Verification Artifact" (file path).
4. KEEP PATHS SIMPLE.

OUTPUT JSON ONLY:
{{
  "skill_used": "skill_name_or_none",
  "steps": [
    {{
      "title": "Setup Project",
      "goal": "Initialize project structure.",
      "artifact": "package.json",
      "type": "ops" 
    }},
    {{
      "title": "Create App Component",
      "goal": "Write the App.tsx file.",
      "artifact": "src/App.tsx",
      "type": "coding"
    }}
  ]
}}
Note: "type" should be "coding" if it involves writing code/files, "ops" for shell commands/scripts.
"""

OPS_PROMPT = """You are an OPS Agent.
Your Goal: {goal}
Current Working Directory: {active_dir}

ROADMAP:
{roadmap}

INSTRUCTIONS:
1. Execute the task using Shell Tools or Skill Scripts.
2. If running "run_skill_script", check the args carefully.
3. ALWAYS chain usage: `cd {active_dir} && <command>`
4. Output [STEP_COMPLETE] when done.

{defensive_alert}
"""

CODING_PROMPT = """You are a CODING Agent.
Your Goal: {goal}
Current Working Directory: {active_dir}

ROADMAP:
{roadmap}

INSTRUCTIONS:
1. Plan the code structure.
2. Use the `write_file` tool.
3. PROTOCOL: You MUST use the `FILE:` format logic (though tool usage is primary).
   If you show code, ensure you CALL `write_file`.

CONTEXT:
{defensive_alert}

Output [STEP_COMPLETE] when verified.
"""

class Orchestrator:
    def __init__(self):
        self.app = MCPApp(name="Industrial_Orchestrator_v3", settings=config_path)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skills_path = os.path.join(base_dir, ".agent", "skills")
        
        self.skill_manager = SkillManager(skills_dir=skills_path)
        self.memory = SessionMemory(os.getcwd())
        self.validator = Validator()

    async def run_manager(self, query: str) -> Dict[str, Any]:
        """Runs Manager to get the Plan."""
        skills = self.skill_manager.discovery.get_all_skills_info()
        instruction = MANAGER_INSTRUCTION.format(query=query, available_skills=skills)
        
        async with self.app.run():
            manager = Agent(name="Manager", instruction=instruction, server_names=["skill-server"])
            async with manager:
                llm = await manager.attach_llm(OpenAIAugmentedLLM)
                response = await llm.generate_str("Create Plan", RequestParams(max_iterations=5))
                try:
                    # Clean JSON
                    json_str = response.strip()
                    if "```json" in json_str: json_str = json_str.split("```json")[1].split("```")[0]
                    elif "```" in json_str: json_str = json_str.split("```")[1].split("```")[0]
                    return json.loads(json_str)
                except Exception as e:
                    logger.error(f"Plan Parsing Failed: {e}")
                    return None

    async def execute_step(self, step: Dict[str, str], retry_count: int):
        """Dispatch and Execute Step."""
        # 1. Update State (Active Directory Check)
        self.memory.update_active_folder() # Follow the cursor
        
        # 2. Defensive Check
        context_alert = ""
        switch = self.validator.detect_context_switch(step['title'], step['goal'])
        if switch['detected']:
            print(f"[Defensive] Context Switch Predicted: {switch['reason']}")
            context_alert = f"[ALERT] This step involves {switch['reason']}. Check for a NEW directory after running."

        # 3. Dispatch Agent
        step_type = step.get('type', 'ops')
        is_coding = step_type == 'coding' or any(k in step['goal'].lower() for k in ['write', 'implement', 'code'])
        
        roadmap = self.memory.get_roadmap()
        
        if is_coding:
            prompt = CODING_PROMPT.format(
                goal=step['goal'], 
                active_dir=self.memory.active_folder,
                roadmap=roadmap,
                defensive_alert=context_alert
            )
            agent_name = f"Coder-{retry_count}"
        else:
            prompt = OPS_PROMPT.format(
                 goal=step['goal'], 
                 active_dir=self.memory.active_folder,
                 roadmap=roadmap,
                 defensive_alert=context_alert
            )
            agent_name = f"Ops-{retry_count}"

        # 4. Execute
        worker = Agent(name=agent_name, instruction=prompt, server_names=["skill-server", "file-tools"])
        async with worker:
            llm = await worker.attach_llm(OpenAIAugmentedLLM)
            response = await llm.generate_str(f"Execute: {step['title']}", RequestParams(max_iterations=15))
            
            # 5. Interventions (Auto-Write)
            missed = self.validator.detect_missed_writes(response)
            if missed:
                print(f"[Intervention] Missed writes detected: {missed}. Fixing...")
                await llm.generate_str(
                    f"You forgot to write these files: {missed}. Call write_file NOW.", 
                    RequestParams(max_iterations=5)
                )

            return response

    async def run(self, query: str):
        print(f"\n⚡ ORCHESTRATOR STARTING: {query}")
        
        # Phase 1: Plan
        plan = await self.run_manager(query)
        if not plan: return
        
        print(f"\n📋 PLAN: {len(plan['steps'])} steps loaded.")

        # Phase 2: Execute
        async with self.app.run(): # Context for workers
            for i, step in enumerate(plan['steps']):
                print(f"\n▶️ STEP {i+1}: {step['title']}")
                print(f"   Goal: {step['goal']}")
                
                success = False
                for attempt in range(3):
                    await self.execute_step(step, attempt)
                    
                    # Phase 3: Verify (Validator)
                    result = self.validator.verify_step_artifacts([step['artifact']], self.memory.active_folder)
                    
                    if result['success']:
                        print(f"   ✅ Verified: {step['artifact']}")
                        self.memory.register_artifact(f"{i+1}", step['artifact'])
                        success = True
                        break
                    else:
                        print(f"   ❌ Failed Verification: {step['artifact']} missing. Retrying...")
                
                if not success:
                    print(f"   ⛔ CRITICAL STOP: Step {i+1} failed.")
                    break
                    
        print("\n✅ MISSION COMPLETE")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else 'build a react app'
    asyncio.run(Orchestrator().run(query))
