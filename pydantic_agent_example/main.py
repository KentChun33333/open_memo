import asyncio
import os
import sys
from dataclasses import dataclass
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Initialize the model using Ollama
# We use OpenAIProvider to specify the local base_url
provider = OpenAIProvider(
    base_url='http://localhost:11434/v1',
    api_key='ollama'
)
model = OpenAIModel('Nemotron-3-nano', provider=provider)

# Define dependencies
@dataclass
class AgentDependencies:
    finance_session: ClientSession
    fs_session: ClientSession

# Initialize the agent
agent = Agent(
    model,
    deps_type=AgentDependencies,
    system_prompt=(
        "You are a helpful assistant with access to financial tools and the local filesystem via MCP. "
        "Use the available tools to answer requests."
    )
)

# --- Finance Tools Wrapper ---
@agent.tool
async def calculate_position_size(ctx: RunContext[AgentDependencies], account_value: float, risk_percent: float, entry_price: float, stop_loss: float) -> str:
    """Calculates position size based on risk parameters."""
    result = await ctx.deps.finance_session.call_tool(
        "calculate_position_size",
        arguments={
            "account_value": account_value,
            "risk_percent": risk_percent,
            "entry_price": entry_price,
            "stop_loss": stop_loss
        }
    )
    return result.content[0].text if result.content else "No output"

@agent.tool
async def get_match_history(ctx: RunContext[AgentDependencies], player_name: str) -> str:
    """Retrieves recent table tennis match results."""
    result = await ctx.deps.finance_session.call_tool(
        "get_match_history",
        arguments={"player_name": player_name}
    )
    return result.content[0].text if result.content else "No output"

@agent.tool
async def get_match_stats(ctx: RunContext[AgentDependencies]) -> str:
    """Returns overall match statistics."""
    result = await ctx.deps.finance_session.call_tool(
        "get_match_stats",
        arguments={}
    )
    return result.content[0].text if result.content else "No output"

# --- Filesystem Tools Wrapper ---
@agent.tool
async def read_file(ctx: RunContext[AgentDependencies], path: str) -> str:
    """Reads the content of a file."""
    result = await ctx.deps.fs_session.call_tool(
        "read_file",
        arguments={"path": path}
    )
    return result.content[0].text if result.content else "No output"

@agent.tool
async def list_directory(ctx: RunContext[AgentDependencies], path: str = ".") -> str:
    """Lists files and directories."""
    result = await ctx.deps.fs_session.call_tool(
        "list_directory",
        arguments={"path": path}
    )
    return result.content[0].text if result.content else "No output"

async def main():
    # Construct absolute paths to the server scripts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    finance_server_path = os.path.join(base_dir, "mcp-server", "my_custom_tools.py")
    fs_server_path = os.path.join(base_dir, "mcp_fs", "server.py")
    
    print(f"Finance Server: {finance_server_path}")
    print(f"FS Server: {fs_server_path}")

    finance_params = StdioServerParameters(command=sys.executable, args=[finance_server_path], env=dict(os.environ))
    fs_params = StdioServerParameters(command=sys.executable, args=[fs_server_path], env=dict(os.environ))

    async with AsyncExitStack() as stack:
        print("Starting Finance Server...")
        finance_transport = await stack.enter_async_context(stdio_client(finance_params))
        finance_read, finance_write = finance_transport
        finance_session = await stack.enter_async_context(ClientSession(finance_read, finance_write))
        await finance_session.initialize()
        
        print("Starting Filesystem Server...")
        fs_transport = await stack.enter_async_context(stdio_client(fs_params))
        fs_read, fs_write = fs_transport
        fs_session = await stack.enter_async_context(ClientSession(fs_read, fs_write))
        await fs_session.initialize()
        
        deps = AgentDependencies(finance_session=finance_session, fs_session=fs_session)
        
        query = "What is my table tennis win rate? Also, list the files in the 'pydantic_agent_example' directory."
        print(f"\nQuery: {query}")
        
        try:
            result = await agent.run(query, deps=deps)
            print(f"\nResult:\n{result.data}")
        except Exception as e:
            print(f"Error running agent: {e}")

if __name__ == "__main__":
    asyncio.run(main())
