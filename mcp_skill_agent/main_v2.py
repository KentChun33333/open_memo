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
from prompt import (
    PLANNER_INSTRUCTION,
    SUBAGENT_INSTRUCTION,
    USER_PROMPT_TEMPLATE,
    AUTO_WRITE_PROMPT
)
from utils import get_logger


logger = get_logger("main_v2")
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
app = MCPApp(name="skill_agent_v2", settings=config_path)

async def run_planning_phase(app, query, available_skills_info):
    """Phase 1: Determine which skill to use."""
    planner_instruction = PLANNER_INSTRUCTION.format(
        available_skills_info=available_skills_info,
        query=query
    )
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
            return None, None

        skill_name = skill_match.group(1).strip()
        task_input = task_match.group(1).strip()
        
        print(f"\nSKILL: {skill_name}")
        print(f"TASK: {task_input}")
        return skill_name, task_input

async def run_discovery_phase():
    """Phase 2 Step 2: Discover available tools from servers."""
    # Create a temporary agent to inspect available tools from all servers
    discovery_agent = Agent(name="discovery", server_names=["skill-server", "file-tools"])
    tool_context_str = "AVAILABLE TOOLS:\n"
    
    async with discovery_agent:
        result = await discovery_agent.list_tools()
        for tool in result.tools:
            # Format: Name (Description)
            tool_context_str += f"- {tool.name}: {tool.description}\n"
    
    logger.info(f"Discovered Tools:\n{tool_context_str}")
    return tool_context_str

async def initialize_sop_agent(app, skill_manager, skill_name):
    """Phase 2 Step 3: Initialize SOP Agent with skill manual."""
    raw_manual = skill_manager.get_skill_content(skill_name)
    
    # New: Get Resource Info for the Tagger
    resources_info = skill_manager.list_skill_contents(skill_name)
    
    from sop_agent import SOPAgent
    sop = SOPAgent(app)
    
    # Initialize SOP with Resources Info (Rule-Based Parsing)
    await sop.initialize(raw_manual, resources_info)
        
    print(f"[SOP Agent] Plan created with {len(sop.steps)} steps.")
    print(sop.get_progress_summary())
    
    # [Task Artifact] Init
    task_md_content = "# Task List\n\n"
    for step in sop.steps:
        task_md_content += f"- [ ] {step.title} <!-- id: {step.id} -->\n"
        
    with open("task.md", "w") as f:
        f.write(task_md_content)
        
    return sop

def resolve_active_folder(shared_context):
    """
    Determines the active working directory based on recent file activity (mtime).
    Scans the workspace for the most recently modified file and sets its directory as active.
    """
    current_active = shared_context.get("active_folder", shared_context["workspace_root"])
    workspace_root = shared_context["workspace_root"]
    
    # Exclusions for the scanner
    IGNORED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', '.agent', 'dist', 'build'}
    IGNORED_FILES = {'.agent_state.json', 'task.md', '.DS_Store'}
    
    latest_mtime = 0
    latest_file_dir = None
    
    try:
        # Walk the workspace to find the latest modified file
        for root, dirs, files in os.walk(workspace_root):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            for file in files:
                if file in IGNORED_FILES or file.startswith('.'):
                    continue
                    
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest_file_dir = root
                except OSError:
                    continue
                    
    except Exception as e:
        print(f"[Smart Resolver] Error scanning workspace: {e}")
        return current_active, None

    # Logic: Switch if we found a valid directory that is deeper/different than root
    if latest_file_dir and latest_file_dir != workspace_root:
        # Don't switch if we are just staying in the same folder, but logging it is fine
        if latest_file_dir != current_active:
             print(f"[Smart Resolver] Context Switch via Activity: {current_active} -> {latest_file_dir}")
             shared_context["active_folder"] = latest_file_dir
             return latest_file_dir, None
        return current_active, None
        
    return current_active, None

async def execute_step_cycle(current_step, sop, skill_name, task_input, active_folder, shared_context, tool_context_str, expectations, detected_root, state_file, pre_step_dirs):
    """Executes a single SOP step using the Manual ReAct Loop."""
    
    context_from_previous = json.dumps(shared_context["artifacts"], indent=2)
    
    # --- DYNAMIC INSTRUCTION ---
    subagent_instruction = SUBAGENT_INSTRUCTION.format(
        task_input=task_input,
        active_folder=active_folder,
        context_from_previous=context_from_previous,
        expectations=json.dumps(expectations, indent=2),
        tool_context_str=tool_context_str
    )
    
    # --- DEFENSIVE CHECK: Root Switch ---
    ctx_switch = sop.detect_context_switch(current_step)
    if ctx_switch["detected"]:
        print(f"[Defensive Check] Potential Context Switch Detected: {ctx_switch['reason']}")
        subagent_instruction = f"""
[ALERT: CONTEXT SWITCH EXPECTED]
This step involves: {ctx_switch['reason']}
It is highly likely that a NEW directory will be created or the context will change.
1. Be aware of the new directory path.
2. Any subsequent file edits MUST be inside the new directory.
3. If you run a script, VERIFY the folder structure afterwards.

""" + subagent_instruction
    
    # --- MANUAL REACT LOOP (DeepCode Pattern) ---
    attempts = 0
    max_step_retries = 2
    step_success = False
    retry_feedback = ""

    while attempts < max_step_retries and not step_success:
        print(f"Running Step {current_step.id} (Attempt {attempts+1})...")

        # Prepare Instruction with Feedback
        current_instruction = subagent_instruction
        if retry_feedback:
            current_instruction += f"\n\n[PREVIOUS FAILURE]: {retry_feedback}\n"
        
        # Create Subagent
        subagent = Agent(
            name=f"Worker-{skill_name}-{current_step.id}-{attempts}",
            instruction=current_instruction,
            server_names=["skill-server", "file-tools"]
        )
        
        async with subagent:
                llm_sub = await subagent.attach_llm(OpenAIAugmentedLLM)
                
                # Initial User Prompt
                user_prompt = USER_PROMPT_TEMPLATE.format(
                    step_id=current_step.id,
                    step_title=current_step.title,
                    step_content=current_step.content,
                    sop_context=sop.get_progress_summary()
                )
                
                # --- MANUAL REACT LOOP (Semi-Autonomous) ---
                react_max_steps = 10  # Number of "Intervention Cycles"
                react_step = 0
                final_response = ""
                
                while react_step < react_max_steps:
                    react_step += 1
                    
                    # Prompt Strategy:
                    current_prompt = user_prompt if react_step == 1 else "Status Update: Continue execution. If all actions are done and verified, output [STEP_COMPLETE]."
                    
                    try:
                        # Allow 5 internal ReAct steps per cycle
                        response = await llm_sub.generate_str(current_prompt, RequestParams(max_iterations=15))
                        final_response = response
                        
                        print(f"  [Cycle {react_step}] Agent Output: {response[:100]}...")
                        
                        # --- INTERVENTION 1: Auto-Write (DeepCode Feature) ---
                        if "```" in response and "write_file" not in response:
                                print(f"  [Intervention] Code blocks detected. Triggering Auto-Write...")
                                aw_prompt = AUTO_WRITE_PROMPT
                                await llm_sub.generate_str(aw_prompt, RequestParams(max_iterations=10))
                        
                        # --- INTERVENTION 2: Completion Check ---
                        if "[STEP_COMPLETE]" in response:
                            break
                            
                    except Exception as e:
                        print(f"  [Cycle {react_step}] Error: {e}")
                        retry_feedback += f"Error in Cycle {react_step}: {e}. "
                        break
                
                # Feedback to verification logic
                response = final_response

                # --- VERIFICATION (Semantic) ---
                new_files = re.findall(r"CREATED_FILE:\s*(.*)", response)
                verified_files = []
                
                # A. Check Reported Files
                if new_files:
                    print(f"Verifying {len(new_files)} reported artifacts...")
                    for f_path in new_files:
                        f_path = f_path.strip()
                        abs_path = os.path.join(active_folder, f_path)
                        
                        if os.path.exists(abs_path) and os.path.getsize(abs_path) > 0:
                            print(f"  [OK] Verified: {f_path} ({os.path.getsize(abs_path)} bytes)")
                            verified_files.append(f_path)
                        else:
                            print(f"  [FAIL] Missing or Empty: {f_path}")
                    
                    if verified_files:
                        shared_context["artifacts"][current_step.id] = verified_files

                # B. Check EXPECTED Files (SOP Metadata)
                missing_expected = []
                for exp in expectations:
                    exp_path = os.path.join(active_folder, exp)
                    if not os.path.exists(exp_path) or os.path.getsize(exp_path) == 0:
                        missing_expected.append(exp)
                        print(f"  [FAIL] Expected Artifact Missing: {exp}")
                    else:
                            print(f"  [OK] Expected Artifact Found: {exp}")

                # Decision
                completed_signal = "[STEP_COMPLETE]" in response
                implicit_success = (len(expectations) > 0 and len(missing_expected) == 0)
                is_script_step = "script" in current_step.title.lower() or "run" in current_step.title.lower()

                if completed_signal or implicit_success or is_script_step:
                    if missing_expected and not is_script_step:
                            print("FAILURE: Critical Expected Artifacts missing.")
                            retry_feedback = f"VALIDATION ERROR: The following required files are missing or empty: {json.dumps(missing_expected)}. Please create them."
                            attempts += 1
                    elif new_files and not verified_files and not is_script_step:
                            print("FAILURE: Hallucinated files.")
                            retry_feedback = "VALIDATION ERROR: You claimed to create files but they are invalid (missing or empty). Check paths and write content."
                            attempts += 1
                    else:
                            # Success
                            step_success = True
                            if is_script_step:
                                print("SUCCESS: Script Execution Auto-Approved (User Policy).")
                            elif not completed_signal:
                                print("SUCCESS: Implicit Completion (All Expected Artifacts Verified).")
                            else:
                                print(f"Step {current_step.id} COMPLETED.")
                            
                            # Auto-Write (DeepCode Feature) check one last time? 
                            # (Already handled in intervention, but safeguard is good)
                            
                            sop.mark_step_done()
                            
                            # --- SMART POST-STEP UPDATE (Snapshot Logic) ---
                            # If we didn't find a marker, try the diff method fallback
                            if not detected_root:
                                try:
                                    post_step_dirs = set([d for d in os.listdir(shared_context["workspace_root"]) 
                                                            if os.path.isdir(os.path.join(shared_context["workspace_root"], d))])
                                    new_dirs = post_step_dirs - pre_step_dirs
                                    if new_dirs:
                                        new_dir = list(new_dirs)[0]
                                        # Only switch if not .git or hidden
                                        if not new_dir.startswith("."):
                                            shared_context["active_folder"] = os.path.join(shared_context["workspace_root"], new_dir)
                                            print(f"[Smart Resolver] Detected new directory (Fallback): {shared_context['active_folder']}")
                                except Exception:
                                    pass

                            # Persist State
                            with open(state_file, "w") as f:
                                json.dump(shared_context, f, indent=2)

                else:
                    print("WARNING: No [STEP_COMPLETE] signal.")
                    retry_feedback = "Step not marked complete. Did you finish?"
                    attempts += 1

    if not step_success:
        print(f"CRITICAL: Step {current_step.id} failed after {max_step_retries} retries.")
        return False
    
    return True

async def main(query):
    # 1. Initialize Helper to get skills list (for Planner)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    skill_manager = SkillManager(skills_dir=skills_path)
    available_skills_info = skill_manager.discovery.get_all_skills_info()

    # --- PHASE 1: PLANNING ---
    skill_name, task_input = await run_planning_phase(app, query, available_skills_info)
    if not skill_name:
        return

    # --- PHASE 2: EXECUTION (SOP-GUIDED PULL MODEL) ---
    print("\n========== PHASE 2: EXECUTION (SOP GUIDED) ==========")
    

    # --- 1. Dynamic Tool Discovery ---
    tool_context_str = await run_discovery_phase()
    
    # --- 2. Initialize SOP Agent (Master) ---
    sop = await initialize_sop_agent(app, skill_manager, skill_name)

    # --- 3. Execution Loop (Stateful) ---
    # INDUSTRIAL PRACTICE: Shared State & Persistence
    shared_context = {
        "workspace_root": os.path.abspath(os.getcwd()),
        "artifacts": {}, # Maps step_id -> [files]
        "logs": []
    }
    state_file = ".agent_state.json"
    
    while not sop.is_finished():
        current_step = sop.get_current_step()
        if not current_step: break
        
        print(f"\n--- EXECUTION: Step {current_step.id} [{current_step.title}] ---")
        
        # --- 1. ACTIVE FOLDER DETECTION ---
        active_folder, detected_root = resolve_active_folder(shared_context)
        
        # Snapshot directories (Secondary Heuristic)
        try:
            pre_step_dirs = set([d for d in os.listdir(shared_context["workspace_root"]) 
                                    if os.path.isdir(os.path.join(shared_context["workspace_root"], d))])
        except Exception:
            pre_step_dirs = set()

        expectations = getattr(current_step, "expected_artifacts", []) # Use new metadata
        
        # --- 2. EXECUTE STEP ---
        success = await execute_step_cycle(
            current_step, sop, skill_name, task_input, active_folder, 
            shared_context, tool_context_str, expectations, 
            detected_root, state_file, pre_step_dirs
        )
        
        if not success:
            break

    print("\n========== MISSION COMPLETE ==========")

if __name__ == "__main__":
    query = 'please build a web artifact that example the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    asyncio.run(main(query))
