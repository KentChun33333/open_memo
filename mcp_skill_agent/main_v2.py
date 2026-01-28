import asyncio
import os
import sys
import re
import logging
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from skill_manager import SkillManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stderr
)
# Reduce noise
logging.getLogger("mcp_agent").setLevel(logging.WARNING) 

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
app = MCPApp(name="skill_agent_v2", settings=config_path)

async def main(query):
    # 1. Initialize Helper to get skills list (for Planner)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    skill_manager = SkillManager(skills_dir=skills_path)
    available_skills_info = skill_manager.discovery.get_all_skills_info()

    # --- PHASE 1: PLANNING ---
    planner_instruction = f"""You are the PLANNER Agent.
Your goal is to delegate the work to a single Specialized Subagent.

Available Skills:
{available_skills_info}

INSTRUCTIONS:
1. Analyze the user's request: "{query}"
2. Decide which SINGLE skill is best suited.
3. OUTPUT in this format:
   SKILL_NAME: <exact name>
   SUBAGENT_TASK: <specific instructions>
"""
    print("\n========== PHASE 1: PLANNING ==========")
    async with app.run():
        planner = Agent(
            name="planner",
            instruction=planner_instruction,
            server_names=["skill-server"] 
        )
        async with planner:
            llm_planner = await planner.attach_llm(OpenAIAugmentedLLM)
            planner_output = await llm_planner.generate_str(f"Plan for: {query}")
            print(f"[Planner]:\n{planner_output}\n")

        # Parse Output
        skill_match = re.search(r"SKILL_NAME:\s*(.+)", planner_output)
        task_match = re.search(r"SUBAGENT_TASK:\s*(.+)", planner_output, re.DOTALL)
        
        if not skill_match or not task_match:
            print("Error: Could not parse planner output.")
            return

        skill_name = skill_match.group(1).strip()
        task_input = task_match.group(1).strip()
        
        print(f"\nSKILL: {skill_name}")
        print(f"TASK: {task_input}")

        # --- PHASE 2: EXECUTION (SOP-GUIDED PULL MODEL) ---
        print("\n========== PHASE 2: EXECUTION (SOP GUIDED) ==========")
        
        # 1. Get Manual Content
        raw_manual = skill_manager.get_skill_content(skill_name)
        
        # 2. Parse into SOP
        from sop_agent import SOPParserAgent, SOPController
        sop_agent = SOPParserAgent(app)
        
        # We need a temporary context for the parser
        async with app.run():
            steps = await sop_agent.parse(raw_manual)
            
        sop = SOPController(steps)
        print(f"[SOP Controller] Loaded {len(steps)} steps.")
        print(sop.get_progress_summary())

        # 3. Execution Loop
        subagent_instruction = f"""You are a Universal Skill-Based Agent.
Assignment: {task_input}

PROTOCOL:
1. You are assigned a SPECIFIC STEP from the Standard Operating Procedure (SOP).
2. Focus ONLY on completing that step.
3. Use `run_skill_script` to execute the necessary scripts.
4. Use `read_skill_reference` if you need to check specific parameter docs.
5. Report "STEP_COMPLETE" when you have successfully verified the step's outcome.
"""
        
        async with app.run():
            subagent = Agent(
                name=f"Worker-{skill_name}",
                instruction=subagent_instruction,
                server_names=["skill-server", "bash-tools"]
            )

            async with subagent:
                llm_sub = await subagent.attach_llm(OpenAIAugmentedLLM)
                
                while not sop.is_finished():
                    current_step = sop.get_current_step()
                    if not current_step: break
                    
                    print(f"\n--- EXECUTION: Step {current_step.id} [{current_step.title}] ---")
                    
                    # Context for the LLM
                    context = sop.build_prompt_context()
                    
                    user_prompt = f"""
CURRENT SITUATION:
{context}

YOUR TASK:
Execute Step {current_step.id}. 
- RUN scripts if required.
- VERIFY files if required.
- DO NOT hallucinate completion.

When finished, output: [STEP_COMPLETE]
"""
                    # Robust execution
                    response = await llm_sub.generate_str(user_prompt, RequestParams(max_iterations=8))
                    print(f"[Worker Output]: {response}")

                    # Check for completion signal
                    if "[STEP_COMPLETE]" in response or "STEP_COMPLETE" in response:
                        print(f"Step {current_step.id} MARKED COMPLETE.")
                        sop.advance_step()
                    else:
                        print(f"Step {current_step.id} NOT marked complete. Retrying...")
                        pass
                        
        print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = 'please build a web artifact that example the MCP'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
