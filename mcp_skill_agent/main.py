import asyncio
import os
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from skill_manager import SkillManager
import logging
import sys

# Path to config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# Initialize app
app = MCPApp(name="skill_agent", settings=config_path)

# Configure logging to show our logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stderr
)
# Optionally set mcp_agent logs to WARNING if they are too noisy, 
# but keep skill_manager at INFO
logging.getLogger("mcp_agent").setLevel(logging.INFO) 
logging.getLogger("skill_manager").setLevel(logging.INFO)


async def main(query):
    # Load initial skill awareness to inject into system prompt
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    skill_manager = SkillManager(skills_dir=skills_path)
    
    available_skills_info = skill_manager.get_all_skills_info()
    
    # helper for subagent execution
    async def run_skill_as_subagent(skill_name: str, task_input: str):
        print(f"\n[Subagent] Spawning specialized agent for '{skill_name}'...")
        
        # 1. Get specialized instruction
        instruction = skill_manager.get_skill_instruction(skill_name)
        
        # 2. Create subagent
        subagent = Agent(
            name=f"Subagent-{skill_name}",
            instruction=instruction + """
            
            IMPORTANT WORKFLOW RULES:
            1. **Step-by-Step Execution**: You MUST implicitly follow the protocol in the Skill's "Instructions" above.
               - If the skill has Steps 1, 2, and 3, you MUST execute ALL of them.
               - DO NOT STOP after the first successful script execution.
            2. **Verification**: After running a script (like `init-artifact`), you MUST:
               - Proceed to the NEXT step (e.g., Development/Bundling).
            3. **Completion**: You are NOT done until you have produced the FINAL artifact (e.g., the bundled HTML file).
            4. **Tool Usage**:
               - Only Use `run_skill_script` for skill actions.
            """,
            # Subagent needs skill-server (for run_skill_script) and bash-tools
            server_names=["skill-server", "code-server"] 
        )
        
        # 3. Attach LLM and run with High Stamina (REPL Mode)
        async with subagent:
            # Solution 1: We cannot pass max_iterations here (API limitation), so we rely on the Protocol + Verification Loop
            llm_sub = await subagent.attach_llm(OpenAIAugmentedLLM)
            print(f"[Subagent] Starting task: {task_input}")
            
            # Solution 3: Outer Verification Loop (The "Manager" Check)
            # We treat the first run as the attempt.
            response = await llm_sub.generate_str(
                f"Please complete this task: {task_input}", RequestParams(max_iterations=35))
            
            if len(response) < 50: 
                 print("[Subagent] Output too short, forcing verification...")
                 response = await llm_sub.generate_str("Are you sure you completed the MANDATORY STEP?")
            
            return response

    # --- PROMPTS ---
    
    # 1. Planner System Prompt - Simplified for Subagent Delegation
    planner_instruction = f"""You are the PLANNER Agent.
Your goal is to analyze the user's request and delegate the work to a single Specialized Subagent.

Available Skills:
{available_skills_info}

INSTRUCTIONS:
1. Analyze the user's request: "{query}"
2. Explore skills using `activate_skill` if you need to check capabilities.
3. Decide which SINGLE skill is best suited for this task.
4. Formulate a specific, self-contained TASK PROMPT for that subagent.
   - The task prompt should contain all necessary details (project name, requirements) extracted from the user's request.
5. OUTPUT your decision in this strict format:
   
   SKILL_NAME: <exact name of the skill>
   SUBAGENT_TASK: <detailed instructions for the subagent>

   Examples:
   SKILL_NAME: web-artifacts-builder
   SUBAGENT_TASK: Initialize a new project called 'dashboard' and bundle it.

   SKILL_NAME: skill-creator
   SUBAGENT_TASK: Create a new skill called 'weather-cli' that wraps the curl command.
"""

    async with app.run():
        # --- PHASE 1: PLANNING ---
        print("\n========== PHASE 1: PLANNING (DELEGATION) ==========")
        planner = Agent(
            name="planner_agent",
            instruction=planner_instruction,
            server_names=["skill-server", "bash-tools"] 
        )
        
        planner_output = ""
        
        async with planner:
            llm_planner = await planner.attach_llm(OpenAIAugmentedLLM)
            
            # Run planning
            print(f"Goal: {query}")
            planner_output = await llm_planner.generate_str(f"Decide which skill to use for: {query}")
            print(f"\n[Planner Output]:\n{planner_output}\n")

        # --- PHASE 2: SUBAGENT EXECUTION ---
        print("\n========== PHASE 2: SUBAGENT EXECUTION ==========")
        
        # Parse Planner Output
        import re
        skill_match = re.search(r"SKILL_NAME:\s*(.+)", planner_output)
        task_match = re.search(r"SUBAGENT_TASK:\s*(.+)", planner_output, re.DOTALL)
        
        if skill_match and task_match:
            skill_name = skill_match.group(1).strip()
            task_input = task_match.group(1).strip()
            
            if skill_name == "None" or "No skill" in skill_name:
                print("Planner determined no skill is suitable.")
            else:
                 result = await run_skill_as_subagent(skill_name, task_input)
                 print(f"\n[Subagent Final Result]:\n{result}")
        else:
            print("[Error] Could not parse SKILL_NAME or SUBAGENT_TASK from Planner output.")
            print("Raw Output:", planner_output)


if __name__ == "__main__":
    query = """
    please build a web artifact that example the MCP, 
    where you need to follow the step-by-step instructions 
    """
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
