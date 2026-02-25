import sys
import os
import asyncio

# Fix import path to include parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_skill_agent.orchestrator import Orchestrator

def main():
    """
    Main Entry Point for the Production Skill Agent.
    Delegates lifecycle management to the Orchestrator.
    """
    query = 'please leaverage skill of web-artifact-builder to build a web artifact with example of the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    
    print(f"Starting Production Agent with Query: {query}")
    
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(query))

if __name__ == "__main__":
    main()
