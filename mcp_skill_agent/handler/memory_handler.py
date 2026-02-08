import os
import glob
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
try:
    from ..orchestrator.structs import SessionMemory
except ImportError:
    from orchestrator.structs import SessionMemory

logger = logging.getLogger(__name__)

class SessionMemoryManager:
    """
    Global State Manager for the Industrial Agent.
    Manages the SessionMemory dataclass and handles persistence.
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        
        # Initialize in-memory session
        self.memory = SessionMemory(
            workspace_root=self.workspace_root,
            cwd_rel="."
        )



    def update_active_folder(self, new_dir: Optional[str] = None):
        """
        Updates active_folder (via cwd_rel).
        """
        target_dir = None
        
        if new_dir:
            abs_path = os.path.abspath(os.path.join(self.memory.active_folder, new_dir))
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                target_dir = abs_path
        
        if not target_dir:
            target_dir = self._scan_for_activity()
            
        if target_dir and target_dir != self.memory.active_folder:
            logger.info(f"SessionMemory: Switching active folder to {target_dir}")
            self.memory.active_folder = target_dir # Uses the setter to update cwd_rel

    def set_active_folder(self, new_dir: str):
        """Sets active folder explicitly (absolute or relative)."""
        if not new_dir:
            return
        self.memory.active_folder = new_dir

    def set_project_root(self, project_root: str):
        """Sets project root and aligns active folder to it."""
        if not project_root:
            return
        self.memory.project_root = os.path.abspath(project_root)
        self.set_active_folder(self.memory.project_root)

    def _scan_for_activity(self) -> Optional[str]:
        """Scans workspace for most recently modified file."""
        IGNORED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', '.agent', 'dist', 'build', 'memory'}
        IGNORED_FILES = {'.agent_state.json', 'task.md', '.DS_Store'}
        
        latest_mtime = 0
        latest_file_dir = None
        
        try:
            # We explicitly scan from workspace root to catch changes anywhere
            for root, dirs, files in os.walk(self.memory.workspace_root):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                for file in files:
                    if file in IGNORED_FILES or file.startswith('.'): continue
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        if mtime > latest_mtime:
                            latest_mtime = mtime
                            latest_file_dir = root
                    except OSError:
                        continue
        except Exception:
            return None
            
        return latest_file_dir

    def save_plan(self, steps: List[Any]):
        """
        Persists the Execution Plan (List of SkillSteps).
        Converts dataclasses to dicts for storage.
        """
        try:
            # Check if steps are dataclasses, convert if so
            plan_data = []
            for s in steps:
                if hasattr(s, "__dataclass_fields__"):
                    plan_data.append(asdict(s))
                elif isinstance(s, dict):
                    plan_data.append(s)
                else:
                    logger.warning(f"Unknown step format: {type(s)}")
            
            self.memory.plan = plan_data
            logger.info("Execution Plan saved to SessionMemory.")
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")

    def get_plan(self) -> List[Dict[str, Any]]:
        """Retrieves the persisted execution plan."""
        return self.memory.plan

    def update_step_status(self, step_id: int, status: str):
        """Updates the status of a specific step in the plan."""
        for step in self.memory.plan:
            if step.get("id") == step_id:
                step["status"] = status

    def persist_plan_to_file(self, plan: Any, query: str):
        """
        Saves the execution plan to a dedicated JSON file for logging/debugging.
        Path: <workspace>/.agent/memory/plans/plan_<timestamp>.json
        """
        try:
            import time
            timestamp = int(time.time())
            plans_dir = os.path.join(self.workspace_root, ".agent", "memory", "plans")
            os.makedirs(plans_dir, exist_ok=True)
            
            filename = f"plan_{timestamp}.json"
            filepath = os.path.join(plans_dir, filename)
            
            # Convert dataclass to dict if needed
            plan_data = []
            steps = plan.steps if hasattr(plan, "steps") else plan
            
            for s in steps:
                 if hasattr(s, "__dataclass_fields__"):
                     plan_data.append(asdict(s))
                 elif isinstance(s, dict):
                     plan_data.append(s)
            
            output = {
                "timestamp": timestamp,
                "query": query,
                "steps": plan_data
            }
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2)
                
            logger.info(f"Plan persisted to {filepath}")
        except Exception as e:
            logger.error(f"Failed to persist plan to file: {e}")

    def update_clipboard(self, path: str, content: str):
        """Updates the clipboard with file content, ensuring persistence."""
        # Normalize path to relative if possible for cleaner keys, or keep abs?
        # Let's verify if path is absolute or relative
        # Ideally we store relative paths if within workspace
        store_key = path
        if os.path.isabs(path) and path.startswith(self.workspace_root):
             store_key = os.path.relpath(path, self.workspace_root)
        
        self.memory.clipboard[store_key] = content

    def get_clipboard(self) -> Dict[str, str]:
        """Returns the current clipboard."""
        return self.memory.clipboard

    def register_artifact(self, step_id: str, file_path: str):
        """Registers a created file to a step ID."""
        if step_id not in self.memory.artifacts:
            self.memory.artifacts[step_id] = []
        
        # Ensure absolute path for consistency
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.memory.active_folder, file_path))
            
        if file_path not in self.memory.artifacts[step_id]:
            self.memory.artifacts[step_id].append(file_path)



    def log_tool_usage(self, agent_name: str, step_id: int, cycle: int, tool_name: str, args: Dict[str, Any]):
        """Logs tool usage for a given step and cycle."""
        self.memory.tool_history.append({
            "agent_name": agent_name,
            "step_id": step_id,
            "cycle": cycle,
            "tool_name": tool_name,
            "args": args
        })

    def log_agent_feedback(self, step_id: int, agent_name: str, feedback: str, feedback_type: str):
        """
        Logs feedback from an agent (e.g., Critic, Tech Lead) for a given step.
        
        Args:
            step_id: The ID of the step this feedback relates to.
            agent_name: Name of the agent providing feedback (e.g., "Technical-Critic").
            feedback: The full feedback text.
            feedback_type: Type of feedback (e.g., "APPROVED", "REJECTED").
        """
        self.memory.agent_feedback_history.append({
            "step_id": step_id,
            "agent_name": agent_name,
            "feedback": feedback,
            "feedback_type": feedback_type
        })
        logger.info(f"Agent feedback logged: {agent_name} -> {feedback_type} for step {step_id}")

    def get_tool_history(self, step_id: int) -> List[List[str]]:
        """Returns tool usage grouped by cycle for a step."""
        filtered = [h for h in self.memory.tool_history if h.get("step_id") == step_id]
        if not filtered:
            return []
        # Group tools by cycle
        cycles: Dict[int, List[str]] = {}
        for h in filtered:
            c = int(h.get("cycle", 0))
            cycles.setdefault(c, []).append(h.get("tool_name", ""))
        return [cycles[c] for c in sorted(cycles.keys())]

    def get_roadmap(self) -> str:
        """Generates a concise tree view of the active folder using glob."""
        tree_lines = []
        active_dir = self.memory.active_folder
        
        # Define ignored directories
        IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist", "build", "memory"}
        
        # Root display
        display_name = os.path.basename(active_dir) or active_dir
        tree_lines.append(f"📂 {display_name}/ (Current)")
        
        def process_directory(path: str, current_level: int, max_level: int = 2):
            try:
                # Use glob to find all items in the current directory
                items = sorted(glob.glob(os.path.join(path, "*")))
            except Exception:
                return

            sub_dirs = []
            sub_files = []
            
            for item in items:
                name = os.path.basename(item)
                if name.startswith("."): continue
                
                if os.path.isdir(item):
                    if name not in IGNORED_DIRS:
                        sub_dirs.append(item)
                else:
                    sub_files.append(item)
            
            # Print files
            file_indent = "  " * (current_level + 1)
            for i, f in enumerate(sub_files):
                if i > 8:
                    tree_lines.append(f"{file_indent}... ({len(sub_files)-8} more file(s))")
                    break
                tree_lines.append(f"{file_indent}📄 {os.path.basename(f)}")
            
            # Recurse into directories
            next_level = current_level + 1
            if next_level <= max_level:
                for d in sub_dirs:
                    dir_name = os.path.basename(d)
                    dir_indent = "  " * next_level
                    tree_lines.append(f"{dir_indent}� {dir_name}/")
                    process_directory(d, next_level, max_level)

        process_directory(active_dir, 0)
        return "\n".join(tree_lines)

    def get_recent_file_paths(self, lookback_steps: int = 2) -> List[str]:
        """
        Retrieves file paths accessed in the last `lookback_steps` distinct steps.
        
        Args:
            lookback_steps (int): Number of previous distinct steps to consider.
            
        Returns:
            List[str]: List of unique file paths accessed.
        """
        paths = set()
        seen_step_ids = set()
        
        # Iterate backwards through tool history
        for entry in reversed(self.memory.tool_history):
            step_id = entry.get("step_id")
            tool_name = entry.get("tool_name", "")
            args = entry.get("args", {})
            
            # If we've collected enough steps and this is a new one, stop
            if len(seen_step_ids) >= lookback_steps and step_id not in seen_step_ids:
                break
                
            seen_step_ids.add(step_id)
            
            # Check for file read tools
            if tool_name in ["read_file", "read_multiple_files"]:
                # Try to extract paths
                # Handle single 'path'
                if "path" in args and isinstance(args["path"], str):
                    paths.add(args["path"])
                    
                # Handle list 'paths'
                if "paths" in args and isinstance(args["paths"], list):
                    for p in args["paths"]:
                        if isinstance(p, str):
                            paths.add(p)
                            
        return list(paths)

    def get_clipboard_subset(self, paths: List[str]) -> Dict[str, str]:
        """
        Returns a subset of the clipboard containing only the specified paths.
        Handles relative/absolute path matching.
        """
        subset = {}
        
        # Normalize request paths to keys used in clipboard
        # The clipboard logic tries to store relative paths if within workspace
        # We need to be robust in matching
        
        normalized_paths = set()
        for p in paths:
             # Add raw
             normalized_paths.add(p)
             # Add relative if absolute
             if os.path.isabs(p) and p.startswith(self.workspace_root):
                 normalized_paths.add(os.path.relpath(p, self.workspace_root))
             # Add absolute if relative
             elif not os.path.isabs(p):
                 normalized_paths.add(os.path.join(self.workspace_root, p))
                 
        for key, content in self.memory.clipboard.items():
            # Check if key (which might be rel or abs) matches any of our target paths
            # We explicitly check direct match, or normalized match
            
            # 1. Exact match
            if key in normalized_paths:
                subset[key] = content
                continue
                
            # 2. Key is relative, check if its absolute matches
            key_abs = key
            if not os.path.isabs(key):
                key_abs = os.path.join(self.workspace_root, key)
                
            if key_abs in [p if os.path.isabs(p) else os.path.join(self.workspace_root, p) for p in normalized_paths]:
                 subset[key] = content
                 
        return subset
