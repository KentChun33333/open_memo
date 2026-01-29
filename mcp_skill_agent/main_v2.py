import asyncio
import os
import sys
import re
import json
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
logger = logging.getLogger("main_v2")

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
        
        # --- 1. Initialize Application ---
        # Load configuration explicitly to ensure servers are connected
        # config_path = os.path.join(os.getcwd(), 'mcp_skill_agent/config.yaml') # This is already done globally
        # app = MCPApp(name="mcp_driver", settings=config_path) # This is already done globally

        # async with app.run(): # Already in app.run() context
        logger.info("MCP Application Started.")

        # --- 2. Dynamic Tool Discovery ---
        # Create a temporary agent to inspect available tools from all servers
        discovery_agent = Agent(name="discovery", server_names=["skill-server", "file-tools"])
        tool_context_str = "AVAILABLE TOOLS:\n"
        
        async with discovery_agent:
            result = await discovery_agent.list_tools()
            for tool in result.tools:
                # Format: Name (Description)
                tool_context_str += f"- {tool.name}: {tool.description}\n"
        
        logger.info(f"Discovered Tools:\n{tool_context_str}")
        
        # --- 3. Initialize SOP Agent (Master) ---
        raw_manual = skill_manager.get_skill_content(skill_name)
        
        # New: Get Resource Info for the Tagger
        resources_info = skill_manager.list_skill_contents(skill_name)
        
        from sop_agent import SOPAgent
        sop = SOPAgent(app)
        
        # Initialize SOP with Resources Info (Rule-Based Parsing)
        # Note: We do NOT pass tool_context_str here anymore per user request.
        await sop.initialize(raw_manual, resources_info)
            
        print(f"[SOP Agent] Plan created with {len(sop.steps)} steps.")
        print(sop.get_progress_summary())
        
        # [Task Artifact] Init
        task_md_content = "# Task List\n\n"
        for step in sop.steps:
            task_md_content += f"- [ ] {step.title} <!-- id: {step.id} -->\n"
            
        with open("task.md", "w") as f:
            f.write(task_md_content)

        # --- 4. Execution Loop (Master-Worker) ---
        subagent_instruction = f"""You are an AUTONOMOUS EXECUTION SUBAGENT.
Your role is to ACTUALLY DO the work, not to describe how to do it.
You are non-interactive. There is no human user watching your output to learn.

Assignment: {task_input}

{tool_context_str}

CRITICAL PROTOCOL:
1. ACTION OVER WORDS: Do not generate tutorials, guides, or explanations.
2. USE TOOLS: You must use available tools to CHANGE THE SYSTEM STATE.
3. RAW EXECUTION: If a step says "Write code", actually call `write_file` with the code. If it says "Run script", call `run_skill_script`.
4. NO CHATTER: Do not output "Here is the code" or "I will now do this". Just call the tool.
5. COMPLETION: Only when the tool execution is confirmed successful, output "STEP_COMPLETE".

NOTICE:
Do not place any artifact files outside of current folder.
"""
        while not sop.is_finished():
                current_step = sop.get_current_step()
                if not current_step: break
                
                print(f"\n--- EXECUTION: Step {current_step.id} [{current_step.title}] ---")
                
                retry_count = 0
                max_retries = 3
                retry_constraint = ""

                while retry_count < max_retries:
                    # Dynamic instruction with history constraint if retrying
                    current_instruction = subagent_instruction
                    if retry_constraint:
                         current_instruction += f"\n\n[HISTORY WARNING]:\n{retry_constraint}\n"

                    # 1. New Agent for FRESH Context per attempt/step
                    subagent = Agent(
                        name=f"Worker-{skill_name}-{current_step.id}-{retry_count}",
                        instruction=current_instruction,
                        server_names=["skill-server", "file-tools"]
                    )

                    async with subagent:
                        llm_sub = await subagent.attach_llm(OpenAIAugmentedLLM)
                        
                        # Context for the LLM
                        user_prompt = f"""
STEP ID: {current_step.id}
ACTION: {current_step.title}
DETAILS:
{current_step.content}

CONTEXT (SOP):
{sop.get_progress_summary()}

INSTRUCTION:
Perform the ACTION defined in DETAILS immediately.
If it is a command, RUN IT.
HINT: Scripts in `scripts/` are bundled with the skill. You do not need to verify their existence. Just run them.
Then output: [STEP_COMPLETE]
"""
                        # Robust execution
                        print(f"Attempt {retry_count + 1} for Step {current_step.id}...")
                        response = await llm_sub.generate_str(user_prompt, RequestParams(max_iterations=15))
                        print(f"[Worker Output]: {response}")

                        # Check for completion signal
                        if "[STEP_COMPLETE]" in response or "STEP_COMPLETE" in response:
                            print(f"Step {current_step.id} MARKED COMPLETE.")
                            sop.mark_step_done()
                            
                            # [Task Artifact] Update on Completion
                            with open("task.md", "w") as f:
                                f.write(sop.generate_task_markdown())
                            print(f"[Artifact] Updated task.md (Step {current_step.id} Done)")
                            
                            break # Break retry loop, move to next step
                        
                        else:
                            print(f"Step {current_step.id} NOT marked complete. Summarizing failure...")
                            # Ask Agent to summarize what went wrong for the next attempt
                            summary_prompt = "We failed to complete the step. Briefly summarize (1-2 sentences) what went wrong and what should be done differently next time."
                            summary = await llm_sub.generate_str(summary_prompt)
                            retry_constraint = f"Previous attempt failed. Reason: {summary}"
                            print(f"[Retry Summary]: {summary}")
                            
                            retry_count += 1
                
                if retry_count >= max_retries:
                    print(f"CRITICAL FAILURE: Max retries reached for Step {current_step.id}. Stopping.")
                    break
                        
        print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = 'please build a web artifact that example the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
