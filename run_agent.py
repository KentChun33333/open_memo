import sys
import os
import asyncio

# Add current directory to path so we can import mcp_skill_agent
sys.path.append(os.getcwd())

from mcp_skill_agent.orchestrator import Orchestrator

def main():
    """Run the Production Orchestrator from the project root."""
    query = 'please build a web artifact that example the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    
    print(f"Starting Production Agent with Query: {query}")
    
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(query))

if __name__ == "__main__":
    main()
