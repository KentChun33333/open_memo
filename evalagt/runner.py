import sys
import os
import argparse
import asyncio
import json
from pathlib import Path

async def main():
    parser = argparse.ArgumentParser(description="Agent Runner for Evaluation")
    parser.add_argument("--agent-dir", required=True, help="Directory of the agent (e.g. nanobot or nanobot-2)")
    parser.add_argument("--query", required=True, help="The query to run")
    parser.add_argument("--workspace", default="/tmp/agent_eval_workspace", help="Workspace directory")
    args = parser.parse_args()

    # Prepend the agent directory to sys.path to force loading its specific modules
    agent_path = os.path.abspath(args.agent_dir)
    sys.path.insert(0, agent_path)

    # Now import the specific nanobot modules
    from nanobot.bus.queue import MessageBus
    from nanobot.agent.loop import AgentLoop
    from nanobot.session.manager import SessionManager
    from nanobot.config.loader import load_config
    
    # Check if this nanobot version exposes _make_provider in cli.commands
    try:
        from nanobot.cli.commands import _make_provider
        has_make_provider = True
    except ImportError:
        has_make_provider = False
        from nanobot.providers.openai import OpenAIProvider

    workspace_path = Path(args.workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    config = load_config()
    bus = MessageBus()
    
    # Initialize the specific LLM Provider
    if has_make_provider:
        provider = _make_provider(config)
        model = config.agents.defaults.model
    else:
        # Fallback if _make_provider is not available in the older version
        provider = OpenAIProvider(model="gpt-4o")
        model = "gpt-4o"
        
    iterations = getattr(config.agents.defaults, 'max_tool_iterations', 15)
        
    # Initialize the specific agent loop
    loop = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace_path,
        max_iterations=iterations,
        model=model
    )

    try:
        # We use process_direct to get a synchronous string response
        response = await loop.process_direct(content=args.query, session_key="eval:runner")
        
        # We need to extract the trajectory (history of tools used/messages)
        # For simplicity, we can fetch it from the session manager
        session = loop.sessions.get_or_create("eval:runner")
        trajectory = []
        if session:
            for msg in session.messages:
                # Omit system prompt to save space
                if msg["role"] != "system":
                    trajectory.append(msg)
                    
        output = {
            "final_answer": response,
            "trajectory": trajectory
        }
        
        # Print JSON to stdout so main.py can parse it
        print(json.dumps(output))

    except Exception as e:
        output = {
            "final_answer": f"ERROR: {str(e)}",
            "trajectory": []
        }
        print(json.dumps(output))

if __name__ == "__main__":
    asyncio.run(main())
