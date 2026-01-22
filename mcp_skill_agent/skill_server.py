from fastmcp import FastMCP
from skill_manager import SkillManager
import os

# Initialize Skill Manager
# We need to find the .agent directory. Assuming we are running from project root or similar.
# Let's try to locate it relative to this file.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # ../../mcp_skill_agent -> .. -> root
skills_path = os.path.join(base_dir, ".agent", "skills")

skill_manager = SkillManager(skills_dir=skills_path)

# Create the server
mcp = FastMCP("Skill-Loader")

@mcp.tool()
def list_available_skills() -> str:
    """Lists all available skills and their descriptions."""
    return skill_manager.get_all_skills_info()

@mcp.tool()
def activate_skill(skill_name: str) -> str:
    """Activates a skill by loading its detailed instructions and content.
    Use this when you need detailed guidance on a specific topic listed in available skills.
    
    Args:
        skill_name: The name of the skill to load.
    """
    return skill_manager.get_skill_content(skill_name)

@mcp.tool()
def list_skill_contents(skill_name: str) -> str:
    """Lists the bundled resources (scripts, references) for a skill.
    Use this to discover what additional resources a skill provides.
    """
    return skill_manager.list_skill_contents(skill_name)

@mcp.tool()
def read_skill_reference(skill_name: str, reference_path: str) -> str:
    """Reads a reference file from the skill's directory.
    
    Args:
        skill_name: The name of the skill.
        reference_path: Relative path to the reference file (e.g., 'references/docs.md').
    """
    return skill_manager.read_skill_reference(skill_name, reference_path)

@mcp.tool()
def run_skill_script(skill_name: str, script_name: str, args: str = "") -> str:
    """Runs a script from the skill's scripts directory.
    
    Args:
        skill_name: The name of the skill.
        script_name: The name of the script (e.g., 'utils.py').
        args: Space-separated arguments to pass to the script.
    """
    # Simple splitting of args string into list
    arg_list = args.split() if args else []
    return skill_manager.run_skill_script(skill_name, script_name, arg_list)

if __name__ == "__main__":
    mcp.run(transport="stdio")
