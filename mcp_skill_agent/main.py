import asyncio
import os
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from skill_manager import SkillManager

# Path to config
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# Initialize app
app = MCPApp(name="skill_agent", settings=config_path)

import logging
import sys

# Configure logging to show our logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stderr
)



async def main():
    # Load initial skill awareness to inject into system prompt
    # We re-instantiate SkillManager here just to read metadata for the prompt.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, ".agent", "skills")
    skill_manager = SkillManager(skills_dir=skills_path)
    
    available_skills_info = skill_manager.get_all_skills_info()
    
    system_instruction = f"""You are a helpful assistant powered by the Agentskill Protocol.
You have access to a library of High-Quality Skills. 
By default, you have the summaries of these skills.
When a user asks a question that matches a skill's domain, use the `activate_skill` tool to load the full instructions.
You also have access to a filesystem server (`filesystem-server`). 
When a skill or user request requires creating files or directories, use the tools from `filesystem-server` (e.g., `write_file`) to actually perform the actions.

Available Skills:
{available_skills_info}
"""

    async with app.run():
        agent = Agent(
            name="skill_aware_agent",
            instruction=system_instruction,
            server_names=["skill-server"],
        )
        async with agent:
            # Attach LLM
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            # Demonstration Query for Level 3 Support
            query = "please create an agent-skill to let agent can create simple machine learning."
            print(f"Query: {query}")
            response = await llm.generate_str(query)
            print(f"Response:\n{response}")

        agent2 = Agent(
            name="file_editor_agent",
            instruction="You are a file editor agent, you can edit and create files and directories.",
            server_names=["filesystem-server"],
        )
        async with agent2:
            # Attach LLM
            llm = await agent2.attach_llm(OpenAIAugmentedLLM)
            
            # Demonstration Query for Level 3 Support
            query = f"base on the response as follow {response}, please create file or edit file accordingly."
            print(f"Query: {query}")
            response = await llm.generate_str(query)
            print(f"Response:\n{response}")

if __name__ == "__main__":
    asyncio.run(main())
