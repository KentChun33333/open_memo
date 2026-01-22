import os
import glob
import yaml
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
import sys

logger = logging.getLogger(__name__)

@dataclass
class SkillMetadata:
    name: str
    description: str
    path: str

class SkillManager:
    def __init__(self, skills_dir: str = ".agent/skills"):
        # Resolves to absolute path relative to the workspace root if typical, 
        # but here we assume the script runs from root or we find the root.
        # Let's try to be robust about finding the .agent directory.
        self.skills_dir = os.path.abspath(skills_dir)
        self.skills: Dict[str, SkillMetadata] = {}
        self._load_skills()

    def _load_skills(self):
        """Scans the skills directory for SKILL.md files and parses frontmatter."""
        pattern = os.path.join(self.skills_dir, "**", "SKILL.md")
        # Recursive search
        skill_files = glob.glob(pattern, recursive=True)
        
        for file_path in skill_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse frontmatter (assumes "---" at start and after frontmatter)
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter_raw = parts[1]
                        metadata = yaml.safe_load(frontmatter_raw)
                        
                        name = metadata.get("name")
                        description = metadata.get("description")
                        
                        if name and description:
                            self.skills[name] = SkillMetadata(
                                name=name,
                                description=description,
                                path=file_path
                            )
            except Exception as e:
                print(f"Error loading skill from {file_path}: {e}")

    def get_skill_names(self) -> List[str]:
        return list(self.skills.keys())

    def get_skill_description(self, name: str) -> Optional[str]:
        skill = self.skills.get(name)
        return skill.description if skill else None

    def get_all_skills_info(self) -> str:
        """Returns a formatted string of all available skills and their descriptions."""
        info = []
        for name, skill in self.skills.items():
            info.append(f"- {name}: {skill.description}")
        return "\n".join(info)

    def get_skill_content(self, name: str) -> str:
        """Returns the full content of the SKILL.md file."""
        logger.info(f"get_skill_content called for skill: {name}")
        skill = self.skills.get(name)
        if not skill:
            msg = f"Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
        
        try:
            with open(skill.path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Successfully read content for skill: {name} ({len(content)} bytes)")
                return content
        except Exception as e:
            msg = f"Error reading skill content: {e}"
            logger.error(msg)
            return msg

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

    def run_skill_script(self, name: str, script_name: str, args: List[str]) -> str:
        """Runs a script from the skill's scripts directory."""
        logger.info(f"run_skill_script called for skill: {name}, script: {script_name}, args: {args}")
        skill = self.skills.get(name)
        if not skill:
            msg = f"Error: Skill '{name}' not found."
            logger.error(msg)
            return msg
            
        skill_dir = os.path.dirname(skill.path)
        script_path = os.path.join(skill_dir, "scripts", script_name)
        
        if not os.path.exists(script_path):
            msg = f"Error: Script '{script_name}' not found in skill '{name}'/scripts."
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
            # Run the script with the skill directory as CWD
            result = subprocess.run(
                cmd, 
                cwd=skill_dir, # Scripts might expect CWD to be skill root
                capture_output=True, 
                text=True, 
                timeout=60 # Increased timeout for potentially long operations
            )
            
            output = ""
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
                err_msg = f"\nExit Code: {result.returncode}"
                output += err_msg
                logger.error(f"Script failed with exit code: {result.returncode}")
                print(f"[SkillManager] {err_msg}", file=sys.stderr)
            else:
                logger.info("Script executed successfully (exit code 0)")
                
            if not output:
                 output = "Script executed successfully with no output."
                 logger.info(output)
                 print(f"[SkillManager] {output}", file=sys.stderr)

            return output
        except Exception as e:
            err_msg = f"Error executing script: {e}"
            logger.error(err_msg)
            print(f"[SkillManager] {err_msg}", file=sys.stderr)
            return err_msg
