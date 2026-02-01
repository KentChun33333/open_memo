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
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.state_file_path = os.path.join(self.workspace_root, ".agent_state.json")
        
        # Load existing state or create new
        self.memory = self.load_state()
        
        # Ensure workspace root matches
        if self.memory.workspace_root != self.workspace_root:
            logger.warning(f"Workspace mismatch in state file. Resetting memory for {self.workspace_root}")
            self.memory = SessionMemory(
                workspace_root=self.workspace_root,
                cwd_rel=".",
                state_file=self.state_file_path
            )
            self.save_state()

    def load_state(self) -> SessionMemory:
        """Loads state from JSON file into SessionMemory object."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r") as f:
                    data = json.load(f)
                    
                    # Migration: Handle 'active_folder' -> 'cwd_rel'
                    cwd_rel = data.get("cwd_rel", ".")
                    if "active_folder" in data and "cwd_rel" not in data:
                        # Convert old absolute path to relative
                        old_active = data["active_folder"]
                        if os.path.isabs(old_active) and old_active.startswith(self.workspace_root):
                            cwd_rel = os.path.relpath(old_active, self.workspace_root)
                    
                    return SessionMemory(
                        workspace_root=data.get("workspace_root", self.workspace_root),
                        cwd_rel=cwd_rel,
                        artifacts=data.get("artifacts", {}),
                        logs=data.get("logs", []),
                        env_vars=data.get("env_vars", {}),
                        step_outputs={int(k): v for k, v in data.get("step_outputs", {}).items()},
                        tool_history=data.get("tool_history", []),
                        current_step_id=data.get("current_step_id", 0),
                        state_file=data.get("state_file", ".agent_state.json")
                    )
            except Exception as e:
                logger.warning(f"Failed to load state: {e}. Creating new session.")
        
        # Default new session
        return SessionMemory(
            workspace_root=self.workspace_root,
            cwd_rel=".",
            state_file=self.state_file_path
        )

    def save_state(self):
        """Persists SessionMemory to JSON file."""
        try:
            with open(self.state_file_path, "w") as f:
                # asdict will exclude property 'active_folder', effectively removing duplication
                json.dump(asdict(self.memory), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

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
            self.save_state()

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

    def log_tool_usage(self, agent_name: str, step_id: int, tool_name: str, args: Dict[str, Any]):
        """Logs a tool execution event to the history."""
        entry = {
            "timestamp": "TODO: Add timestamp", # Simplified for now
            "agent": agent_name,
            "step_id": step_id,
            "tool": tool_name,
            "args": args
        }
        self.memory.tool_history.append(entry)
        # Keep history manageable? Maybe limit size implicitly by file system interaction
        self.save_state()

    def log_agent_feedback(self, step_id: int, agent_name: str, feedback: str, feedback_type: str = "critique"):
        """
        Logs generalized feedback from an agent (Critic, Verifier, Human).
        Schema: {timestamp, step_id, agent_name, feedback, type}
        """
        entry = {
            "timestamp": "TODO: Add timestamp",
            "step_id": step_id,
            "agent_name": agent_name,
            "feedback": feedback,
            "type": feedback_type
        }
        self.memory.agent_feedback_history.append(entry)
        self.save_state()

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
