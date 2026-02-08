import os
import glob
import yaml
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class SkillMetadata:
    name: str
    description: str
    path: str

class SkillDiscovery:
    def __init__(self, skills_dir: str = ".agent/skills"):
        self.skills_dir = os.path.abspath(skills_dir)
        self.skills: Dict[str, SkillMetadata] = {}
        self._load_skills()

    def _load_skills(self):
        """Scans the skills directory for SKILL.md files and parses frontmatter."""
        pattern = os.path.join(self.skills_dir, "**", "SKILL.md")
        skill_files = glob.glob(pattern, recursive=True)
        
        for file_path in skill_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
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
                logger.error(f"Error loading skill from {file_path}: {e}")

    def get_skill_names(self) -> List[str]:
        return list(self.skills.keys())

    def get_skill_metadata(self, name: str) -> Optional[SkillMetadata]:
        return self.skills.get(name)

    def get_all_skills_info(self) -> str:
        """Returns a formatted string of all available skills and their descriptions."""
        info = []
        for name, skill in self.skills.items():
            info.append(f"- {name}: {skill.description}")
        return "\n".join(info)
