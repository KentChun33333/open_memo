import asyncio
import os

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

# Connect to the mcp-server configuration
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_agent.config.yaml")

# Initialize the app with the config path
app = MCPApp(name="my_agent", settings=config_path)

async def main():
    print("Starting agent...")
    async with app.run():
        agent = Agent(
            name="helper",
            instruction="You are a helpful assistant. Use local tools to answer questions about trading and sports.",
            server_names=["my-local-tools", "mcp-fs"],
        )
        async with agent:
            print("Connecting to LLM and Tools...")
            try:
                # Attach LLM - Config should be picked up automatically from context
                llm = await agent.attach_llm(OpenAIAugmentedLLM)
                
                query = "What is my table tennis win rate?"
                print(f"\nQuerying: {query}")
                answer = await llm.generate_str(query)
                print(f"\nAnswer:\n{answer}")

                query_fs = "List the files in the current directory and read the content of 'README.md' (just the first 100 characters)."
                print(f"\nQuerying: {query_fs}")
                answer_fs = await llm.generate_str(query_fs)
                print(f"\nAnswer:\n{answer_fs}")    
            except Exception as e:
                print(f"Error during execution: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
