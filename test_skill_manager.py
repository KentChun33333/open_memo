import sys
import os

# Ensure we can import modules
sys.path.append(os.getcwd())

from mcp_skill_agent.skill_manager import SkillManager

def test_skill_content():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming .agent dir structure relative to root
    skills_path = os.path.join(base_dir, ".agent", "skills")
    
    print(f"Testing SkillManager with path: {skills_path}")
    manager = SkillManager(skills_dir=skills_path)
    
    # We'll test with 'web-artifacts-builder' as we know it exists
    skill_name = "web-artifacts-builder"
    
    print(f"\n--- Fetching content for {skill_name} ---\n")
    content = manager.get_skill_content(skill_name)
    print(content)

if __name__ == "__main__":
    test_skill_content()
