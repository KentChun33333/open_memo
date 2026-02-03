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
        
        server_names = ["skill-server", "file-tools"]
        
        instruction = f"""
        As the best Autonomous Agent over the world.
        you are follow to overall skill protocol to step by step acheive the Main Goal.

        The Skill INSTRUCTIONS:
        {content}

        Main Goal:
        {query}

        You are equil with tools to actually do the work. 

        TOOLS SELECTION:
        1. skill-server: For connected the skill asset, including read the skill.md and its refernece and scripts, execute scripts in skill.md.
        2. file-tools: To explore filesystem, to write and read files, code and assets.
        """
        worker = Agent(name="Worker", instruction=instruction, server_names=server_names)
            
        async with worker:
            llm_worker = await worker.attach_llm(OpenAIAugmentedLLM)
            # We ask it to "Execute and Log"
            resp = await llm_worker.generate_str(f"Please execute the skill to achieve the main goal step by step")
            print(f"[Agent]: {resp}")

    print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = "build a web artifact with introduction of modern agent memory sytem"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
