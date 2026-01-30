import sys
import asyncio
from orchestrator import Orchestrator

def main():
    """
    Main Entry Point for the Production Skill Agent.
    Delegates lifecycle management to the Orchestrator.
    """
    query = 'please build a web artifact that example the Modle context protocol'
    if len(sys.argv) > 1:
        query = sys.argv[1]
    
    print(f"Starting Production Agent with Query: {query}")
    
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run(query))

if __name__ == "__main__":
    main()
