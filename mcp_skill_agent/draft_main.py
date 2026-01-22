import asyncio
import os
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from skill_manager import SkillManager
from fastmcp import FastMCP # Use FastMCP to define the tool easily

# Initialize Skill Manager
# Assuming script runs from a location where .agent/skills is accessible relative to CWD or explicit path.
# We'll assume the script is run from project root.
skill_manager = SkillManager(skills_dir=".agent/skills")

# Create a local FastMCP server for the skill tool
skill_server = FastMCP("Skill-Server")

@skill_server.tool()
def activate_skill(skill_name: str) -> str:
    """Activates a skill by loading its detailed instructions.
    
    Args:
        skill_name: The name of the skill to activate (e.g., 'mcp-agent', 'pptx').
    """
    return skill_manager.get_skill_content(skill_name)

# Config path (reusing the one from mcp_agent_example for simplicity, or we could create a new one)
# We need to add our dynamic skill server to the configuration effectively. 
# Alternatively, since we are using `mcp-agent` library, we can register the tool directly if supported,
# or better yet, run this FastMCP server as a subprocess like the others.
# 
# FOR SIMPLICITY in this "agent creation" task:
# We will start the FastMCP server in background or just assume we can call the function directly?
# The `mcp-agent` architecture expects connection to servers.
# So we need to expose `activate_skill` via a server.
#
# Let's create `skill_tool_server.py` separately or just put it here and run it?
# To integrate with `mcp_agent` workflow, it's best if it's a standalone server script listed in config.

if __name__ == "__main__":
    # If this script is run as main, it acts as the AGENT runner.
    # But we need the TOOL server to be running too.
    # Pattern: Create a separate `tools.py` for the skill server.
    pass
