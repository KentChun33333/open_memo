import os
import glob
import yaml
import logging
import re
from config_loader import config
from typing import Dict, List, Optional
import sys
import time
from skill_discovery import SkillDiscovery, SkillMetadata

logger = logging.getLogger(__name__)

class SkillManager:
    def __init__(self, skills_dir: str = ".agent/skills"):
        # Initialize discovery service
        self.skills_dir = skills_dir
        self.discovery = SkillDiscovery(skills_dir)
    
    @property
    def skills(self) -> Dict[str, SkillMetadata]:
        return self.discovery.skills

    def get_skill_names(self) -> List[str]:
        return self.discovery.get_skill_names()

    def get_skill_description(self, name: str) -> Optional[str]:
        skill = self.discovery.get_skill_metadata(name)
        return skill.description if skill else None

    # Note: get_all_skills_info is REMOVED intentionally as per request to decouple discovery logic.
    # Users should use SkillDiscovery.get_all_skills_info() directly if they need the list.

    def get_skill_content(self, name: str) -> str:
        """Returns the full content of the SKILL.md file and directory structure in raw text format."""
        logger.info(f"get_skill_content called for skill: {name}")
        skill = self.skills.get(name)
        if not skill:
            msg = f"Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
        
        try:
            with open(skill.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use tree view for resource discovery
            skill_dir = os.path.dirname(skill.path)
            tree_view = self._generate_tree_view(skill_dir)
            
            # Format outputs
            output = f"""SKILL: {skill.name}
DESCRIPTION: {skill.description}
PATH: {skill.path}

[DIRECTORY STRUCTURE]
{tree_view}

[INSTRUCTIONS (SKILL.md)]
{content}
"""
            
            logger.info(f"Successfully constructed content for skill: {name}")
            return output

        except Exception as e:
            msg = f"Error reading skill content: {e}"
            logger.error(msg)
            return msg

    def extract_required_scripts_from_content(self, content: str) -> List[str]:
        """Extracts script names referenced in SKILL.md content in order of appearance."""
        if not content:
            return []
        # Capture script references like scripts/init-artifact.sh
        pattern = re.compile(r"scripts/([A-Za-z0-9._-]+\.(?:sh|py|js))")
        matches = pattern.findall(content)
        # Preserve order, dedupe
        ordered = []
        for m in matches:
            if m not in ordered:
                ordered.append(m)
        return ordered

    def get_required_scripts(self, name: str) -> List[str]:
        """Reads SKILL.md and extracts referenced scripts."""
        skill = self.skills.get(name)
        if not skill:
            return []
        try:
            with open(skill.path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.extract_required_scripts_from_content(content)
        except Exception as e:
            logger.error(f"Failed to read SKILL.md for scripts: {e}")
            return []

    def list_skill_contents(self, name: str) -> str:
        """Lists the bundled resources (scripts, references) for a skill."""
        logger.info(f"list_skill_contents called for skill: {name}")
        skill = self.skills.get(name)
        if not skill:
            msg = f"Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
        
        skill_dir = os.path.dirname(skill.path)
        output = [f"Contents of skill '{name}':"]
        
        for subdir in ['scripts', 'references', 'assets']:
             subdir_path = os.path.join(skill_dir, subdir)
             if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                 files = os.listdir(subdir_path)
                 if files:
                     output.append(f"\n[{subdir}]:")
                     for f in files:
                         output.append(f"  - {f}")
        
        if len(output) == 1:
            msg = f"Skill '{name}' has no bundled resources."
            logger.info(msg)
            return msg
            
        result = "\n".join(output)
        logger.info(f"Found resources for skill {name}:\n{result}")
        return result

    def read_skill_reference(self, name: str, reference_path: str) -> str:
        """Reads a reference file from the skill's directory."""
        logger.info(f"read_skill_reference called for skill: {name}, path: {reference_path}")
        skill = self.skills.get(name)
        if not skill:
            msg = f"Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
            
        skill_dir = os.path.dirname(skill.path)
        # Security check: ensure the path is within the listing dir to prevent traversal
        # We assume reference_path is relative to the skill directory, e.g., "references/api_docs.md"
        
        # Simple sanitization
        if ".." in reference_path or reference_path.startswith("/"):
             msg = "Error: Invalid reference path. Must be relative to skill directory."
             logger.error(msg)
             return msg

        full_path = os.path.join(skill_dir, reference_path)
        
        if not os.path.exists(full_path):
            # Fallback: check "references/" subdirectory if not already in path
            if not reference_path.startswith("references/"):
                 fallback_path = os.path.join(skill_dir, "references", reference_path)
                 if os.path.exists(fallback_path):
                     logger.info(f"Reference '{reference_path}' found in subdirectory: {fallback_path}")
                     full_path = fallback_path
                 else:
                     msg = f"Error: Reference '{reference_path}' not found in skill '{name}' (checked root and references/)."
                     logger.error(msg)
                     return msg
            else:
                 msg = f"Error: Reference '{reference_path}' not found in skill '{name}'."
                 logger.error(msg)
                 return msg
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Successfully read reference file: {full_path} ({len(content)} bytes)")
                return content
        except Exception as e:
            msg = f"Error reading reference: {e}"
            logger.error(msg)
            return msg

    def run_skill_script(self, name: str, script_name: str, args: List[str], project_root: Optional[str] = None) -> str:
        """Runs a skill script from the skill-folder, where the command is executed in the project_root folder"""
        start_time = time.time()
        logger.info(f"[SKILL_START] Executing skill '{name}' script '{script_name}' with args: {args} in cwd: {project_root}")
        
        skill = self.skills.get(name)
        if not skill:
            msg = f"[FAILURE] Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
            
        skill_dir = os.path.dirname(skill.path)
        script_path = os.path.join(skill_dir, "scripts", script_name)
        
        if not os.path.exists(script_path):
            msg = f"[FAILURE] Error: Script '{script_name}' not found in skill '{name}'/scripts."
            logger.error(msg)
            return msg
            
        # Determine how to run based on extension (simple implementation)
        import subprocess
        import sys
        
        cmd = []
        if script_path.endswith(".py"):
            cmd = ["python3", script_path] + args
        elif script_path.endswith(".sh"):
            cmd = ["bash", script_path] + args
        elif script_path.endswith(".js"):
             cmd = ["node", script_path] + args
        else:
            # Try to run as executable
            cmd = [script_path] + args
            
        logger.info(f"Executing command: {' '.join(cmd)}")
        # kept for backwards compatibility/direct visibility if needed
        print(f"[SkillManager] Executing: {' '.join(cmd)}", file=sys.stderr)
            
        try:
            # Run the script with the skill directory as CWD? 
            # NO: Users expect outputs in their project root (agent's CWD).
            # Scripts must use __file__ to locate bundled resources.
            # Determine CWD: Use provided project_root or default to current process CWD
            cwd = project_root if project_root and os.path.exists(project_root) else os.getcwd()

            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=config.get("script_execution_timeout", 300) # Default 5 minutes
            )
            
            duration = time.time() - start_time
            output = ""
            status_prefix = ""

            # Always capture stdout
            if result.stdout:
                output += f"Stdout:\n{result.stdout}\n"
                logger.info(f"Script stdout:\n{result.stdout}")
                print(f"[SkillManager] Stdout:\n{result.stdout}", file=sys.stderr)
                
            # Capture stderr if present
            if result.stderr:
                output += f"\nStderr:\n{result.stderr}"
                logger.warning(f"Script stderr:\n{result.stderr}")
                print(f"[SkillManager] Stderr:\n{result.stderr}", file=sys.stderr)
                
            # Capture exit code if failure
            if result.returncode != 0:
                status_prefix = "[FAILURE] "
                err_msg = f"\nExit Code: {result.returncode}"
                output += err_msg
                logger.error(f"[SKILL_END] Script failed with exit code: {result.returncode} (Duration: {duration:.2f}s)")
                print(f"[SkillManager] {err_msg}", file=sys.stderr)
            else:
                status_prefix = "[SUCCESS] "
                logger.info(f"[SKILL_END] Script executed successfully (Duration: {duration:.2f}s)")
                
            if not output:
                 output = "Script executed successfully with no output."
                 logger.info(output)
                 print(f"[SkillManager] {output}", file=sys.stderr)
            return f"{status_prefix}{output}"
        except Exception as e:
            duration = time.time() - start_time
            err_msg = f"[FAILURE] Error executing script: {e}"
            logger.error(f"[SKILL_END] Script execution exception: {e} (Duration: {duration:.2f}s)")
            print(f"[SkillManager] {err_msg}", file=sys.stderr)
            return err_msg

    def _generate_tree_view(self, root_dir: str, max_depth: int = 3, exclude_dirs: List[str] = None) -> str:
        """Generates a tree-like string representation of a directory."""
        if exclude_dirs is None:
            exclude_dirs = []
            
        tree = []
        root_name = os.path.basename(root_dir) or root_dir
        tree.append(f"{root_name}/")
        
        root_dir = os.path.abspath(root_dir)
        
        for root, dirs, files in os.walk(root_dir):
            # Calculate current depth
            rel_path = os.path.relpath(root, root_dir)
            if rel_path == ".":
                level = 0
            else:
                level = rel_path.count(os.sep) + 1
                
            if level >= max_depth:
                # Stop recursing into this directory
                dirs[:] = [] 
                continue

            indent = '│   ' * (level)
            subindent = '│   ' * (level + 1)
            
            # Don't show the root itself again
            if root != root_dir:
                dirname = os.path.basename(root)
                tree.append(f"{indent}├── {dirname}/")
            
            # Filter directories in-place to prevent recursion
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in exclude_dirs]
            files = [f for f in files if not f.startswith('.')]
            
            for i, f in enumerate(files):
                # Simple tree view
                tree.append(f"{subindent}{f}")
                
        return "\n".join(tree)
    
    def get_skill_instruction(self, name: str) -> str:
        """
        Constructs a complete System Instruction for a specialized Subagent.
        It uses the full XML content of the skill (manual + references + scripts list).
        """
        xml_content = self.get_skill_content(name)
        
        instruction = f"""You are a Specialized Subagent for the skill: '{name}'.
Your goal is to complete a specific task using ONLY the tools and scripts provided by this skill.

SKILL CONTEXT:
{xml_content}

INSTRUCTIONS:
1. Understand the user's task.
2. Refer to `[INSTRUCTIONS]` and `[DIRECTORY STRUCTURE]` in the Context above.
3. You have access to `run_skill_script` to execute scripts found in the `<skill_name>/scripts/` directory.
4. DEVELOPER PROTOCOL (CRITICAL):
   - YOU MUST NOT STOP at the template. You MUST customize the code.
   - Continue editing to match the user's request.
5. If a script fails, consult the Manual and retry with corrected arguments.
"""
        return instruction
