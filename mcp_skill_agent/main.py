import asyncio
import os
import sys
import re
import json
import logging
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from skill_manager import SkillManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("main_simple")

# Load Config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
app = MCPApp(name="simple_skill_agent", settings=config_path)

async def main(query):
    print("\n========== SIMPLE SKILL AGENT START ==========")
    
    # 1. Initialize Skill Manager
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    skill_manager = SkillManager(skills_dir=skills_path)
    
    # 2. Planning Phase
    available_skills = skill_manager.discovery.get_all_skills_info()
    planner_prompt = f"""You are a PLANNER.
User Request: "{query}"

Available Skills:
{available_skills}

Select the BEST skill. 
Output format:
SKILL: <skill_name>
"""
    print("Planning...")
    async with app.run():
        planner = Agent(name="Planner", instruction=planner_prompt)
        async with planner:
            llm = await planner.attach_llm(OpenAIAugmentedLLM)
            plan = await llm.generate_str("Analyze request and pick skill.")
            
            match = re.search(r"SKILL:\s*(.+)", plan)
            if not match:
                print("Could not determine skill.")
                return
            skill_name = match.group(1).strip()
            print(f"Selected Skill: {skill_name}")

        # 3. Get Skill Content
        content = skill_manager.get_skill_content(skill_name)
        
        # 4. Simple Step Splitting (Regex)
        # Split by ## or ### headers
        steps_raw = re.split(r"(^|\n)#{2,3}\s+", content)
        # Filter and clean
        steps = []
        for s in steps_raw:
            s = s.strip()
            if len(s) > 20: # arbitrary filter for meaningful content
                # Extract title
                lines = s.split('\n')
                title = lines[0].strip()
                body = "\n".join(lines[1:])
                steps.append({"title": title, "content": body})
        
        print(f"Identified {len(steps)} steps.")

        # 5. Execution Loop (Single Agent)
        # Equip with: skill-server, file-tools, memo-server
        server_names = ["skill-server", "file-tools", "memo-server"]
        
        for i, step in enumerate(steps):
            step_id = i + 1
            print(f"\n--- Step {step_id}: {step['title']} ---")
            
            instruction = f"""You are an Autonomous Agent executing a Skill Step.

CURRENT STEP {step_id}: {step['title']}
INSTRUCTIONS:
{step['content']}

TOOLS SELECTION:
1. skill-server: For connected the skill asset, including read the skill.md and its refernece and scripts, execute scripts in skill.md.
2. file-tools: To explore filesystem, to write and read files, code and assets.
3. memo-server: TO LOG all stdout and stderr, and read history.

CRITICAL PROTOCOL:
1. READ HISTORY: Use `read_history` to understand what happened before (stdout, errors, etc.).
2. EXECUTE: Use skill-server to have read and write.  
3. LOGGING: After execution, you MUST use `log_step` to save your key messages and STDOUT for the next step.
   - log_step(step_id="{step_id}", message="...", stdout="...")

GOAL: Complete the step and log it.
"""
            worker = Agent(name=f"Worker-{step_id}", instruction=instruction, server_names=server_names)
            
            async with worker:
                llm_worker = await worker.attach_llm(OpenAIAugmentedLLM)
                # We ask it to "Execute and Log"
                resp = await llm_worker.generate_str(f"Execute Step {step_id} and log results.")
                print(f"[Agent]: {resp}")

                # we ask for follow ups 
                resp = await llm_worker.generate_str(
                    f"please indentify {resp} as the output the result, and check if need to use write_file to save the result to the designed the folder")


    print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = "build a web artifact"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
