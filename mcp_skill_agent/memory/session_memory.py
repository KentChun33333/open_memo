import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionMemory:
    workspace_root: str
    active_folder: str
    artifacts: Dict[str, List[str]] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    directory_tree: List[str] = field(default_factory=list)
    current_step_id: int = 0
    state_file: str = ".agent_state.json"

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
                active_folder=self.workspace_root,
                state_file=self.state_file_path
            )
            self.save_state()

    def load_state(self) -> SessionMemory:
        """Loads state from JSON file into SessionMemory object."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r") as f:
                    data = json.load(f)
                    # Handle backward compatibility or missing fields
                    return SessionMemory(
                        workspace_root=data.get("workspace_root", self.workspace_root),
                        active_folder=data.get("active_folder", self.workspace_root),
                        artifacts=data.get("artifacts", {}),
                        logs=data.get("logs", []),
                        directory_tree=data.get("directory_tree", []),
                        current_step_id=data.get("current_step_id", 0),
                        state_file=data.get("state_file", ".agent_state.json")
                    )
            except Exception as e:
                logger.warning(f"Failed to load state: {e}. Creating new session.")
        
        # Default new session
        return SessionMemory(
            workspace_root=self.workspace_root,
            active_folder=self.workspace_root,
            state_file=self.state_file_path
        )

    def save_state(self):
        """Persists SessionMemory to JSON file."""
        try:
            with open(self.state_file_path, "w") as f:
                json.dump(asdict(self.memory), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def update_active_folder(self, new_dir: Optional[str] = None):
        """
        Updates active_folder.
        Rules:
        1. If new_dir provided, validate and set.
        2. Else, scan for activity (mtime).
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
            self.memory.active_folder = target_dir
            # Update directory tree when folder changes
            self.memory.directory_tree = self.get_roadmap().split("\n")
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
        """Generates a concise tree view of the active folder."""
        tree_lines = []
        active_dir = self.memory.active_folder
        start_depth = active_dir.rstrip(os.sep).count(os.sep)
        
        for root, dirs, files in os.walk(active_dir):
            current_depth = root.rstrip(os.sep).count(os.sep)
            level = current_depth - start_depth
            
            if level > 2: # Max depth 2 for readability
                continue
            
            # Filter in-place
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "__pycache__", "dist", "build", "memory"]]
            
            indent = "  " * level
            display_name = os.path.basename(root) or root
            if level == 0:
                tree_lines.append(f"📂 {display_name}/ (Current)")
            else:
                tree_lines.append(f"{indent}📂 {display_name}/")
                
            sub_indent = "  " * (level + 1)
            for i, f in enumerate(files):
                if f.startswith("."): continue
                if i > 8: 
                    tree_lines.append(f"{sub_indent}... ({len(files)-8} more file(s))")
                    break
                tree_lines.append(f"{sub_indent}📄 {f}")
                
        return "\n".join(tree_lines)
