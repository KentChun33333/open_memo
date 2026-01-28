import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

try:
    from mcp_skill_agent.bash_tools import mcp
    print("Successfully imported mcp from bash_tools")
    
    # Check if tools are registered
    tools = mcp.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"- {tool.name}")
        
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
