import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SessionMemory:
    """
    Global State Manager for the Industrial Agent.
    Tracks:
    1. Workspace Root (Constant)
    2. Active Working Directory (Dynamic)
    3. Created Artifacts (Per Step)
    4. Execution Logs/History
    """
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.active_folder = self.workspace_root
        
        # Maps step_id -> List[file_paths]
        self.artifacts: Dict[str, List[str]] = {}
        
        # Load state if exists (persistence)
        self.state_file = os.path.join(self.workspace_root, ".agent_state.json")
        self.load_state()

    def update_active_folder(self, new_bound: Optional[str] = None):
        """
        Updates active_folder based on activity scan.
        """
        if new_bound:
            abs_path = os.path.abspath(os.path.join(self.active_folder, new_bound))
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                self.active_folder = abs_path
                self._save_state()
                return

        latest_dir = self._scan_for_activity()
        if latest_dir and latest_dir != self.active_folder:
            logger.info(f"SessionMemory: Switching active folder to {latest_dir}")
            self.active_folder = latest_dir
            self._save_state()

    def _scan_for_activity(self) -> Optional[str]:
        """Scans workspace for most recently modified file."""
        IGNORED_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', '.agent', 'dist', 'build', 'memory'}
        IGNORED_FILES = {'.agent_state.json', 'task.md', '.DS_Store'}
        
        latest_mtime = 0
        latest_file_dir = None
        
        try:
            for root, dirs, files in os.walk(self.workspace_root):
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
        """Registers a created file to a step."""
        if step_id not in self.artifacts:
            self.artifacts[step_id] = []
        
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(self.active_folder, file_path))
            
        if file_path not in self.artifacts[step_id]:
            self.artifacts[step_id].append(file_path)
        
        self._save_state()

    def get_roadmap(self) -> str:
        """Generates a concise tree view of the active folder (Inlined logic)."""
        tree_lines = []
        start_depth = self.active_folder.rstrip(os.sep).count(os.sep)
        
        for root, dirs, files in os.walk(self.active_folder):
            current_depth = root.rstrip(os.sep).count(os.sep)
            level = current_depth - start_depth
            
            if level > 2: # Max depth 2
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

    def _save_state(self):
        state = {
            "workspace_root": self.workspace_root,
            "active_folder": self.active_folder,
            "artifacts": self.artifacts
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    if state.get("workspace_root") == self.workspace_root:
                        self.active_folder = state.get("active_folder", self.workspace_root)
                        self.artifacts = state.get("artifacts", {})
            except Exception:
                pass
