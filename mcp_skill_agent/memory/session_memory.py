import os
import glob
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionMemory:
    workspace_root: str
    cwd_rel: str = "." # Stores relative path from workspace_root
    artifacts: Dict[str, List[str]] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    # directory_tree removed (redundant)
    env_vars: Dict[str, str] = field(default_factory=dict)     # New: Environment Variables
    step_outputs: Dict[int, str] = field(default_factory=dict) # New: Step Outputs
    tool_history: List[Dict[str, Any]] = field(default_factory=list) # New: Tool Execution History
    clipboard: Dict[str, str] = field(default_factory=dict) # New: Cross-step file cache
    plan: List[Dict[str, Any]] = field(default_factory=list) # New: Persisted Execution Plan
    agent_feedback_history: List[Dict[str, Any]] = field(default_factory=list) # New: Generic Feedback History
    current_step_id: int = 0
    state_file: str = ".agent_state.json"

    @property
    def active_folder(self) -> str:
        """Dynamic property to get absolute active folder path."""
        return os.path.abspath(os.path.join(self.workspace_root, self.cwd_rel))

    @active_folder.setter
    def active_folder(self, value: str):
        """Setter to update cwd_rel from an absolute or relative path."""
        if os.path.isabs(value):
            self.cwd_rel = os.path.relpath(value, self.workspace_root)
        else:
            self.cwd_rel = value

class SessionMemoryManager:
    """
    Global State Manager for the Industrial Agent.
    Manages the SessionMemory dataclass and handles persistence.
    """
    # ... (init and load_state methods remain same, will rely on dataclass field addition) ...

    # ... (existing methods) ...

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
            self.save_state()
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
        self.save_state()

    def update_clipboard(self, path: str, content: str):
        """Updates the clipboard with file content, ensuring persistence."""
        # Normalize path to relative if possible for cleaner keys, or keep abs?
        # Let's verify if path is absolute or relative
        # Ideally we store relative paths if within workspace
        store_key = path
        if os.path.isabs(path) and path.startswith(self.workspace_root):
             store_key = os.path.relpath(path, self.workspace_root)
        
        self.memory.clipboard[store_key] = content
        self.save_state()

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
        
        self.save_state()

    def log_event(self, message: str):
        """Appends a log message to the history."""
        self.memory.logs.append(message)
        self.save_state()

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
