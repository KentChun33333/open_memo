#!/usr/bin/env python3
"""
MCP Agent Client - Connects to your local MCP server and provides an interface
for interacting with trading and table tennis tools.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()


class LocalMCPAgent:
    """Agent client for connecting to your local MCP server."""

    def __init__(self, config_path: str = None):
        """Initialize the MCP Agent with local server configuration."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "mcp-config.json")

        self.config_path = config_path
        self.agent = None
        self.client = None

    async def initialize(
        self, model_name: str = "Nemotron-3-nano", temperature: float = 0.7
    ):
        """Initialize the MCP Agent and connect to the local server."""
        try:
            # Check Ollama server availability
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            if not self._check_ollama_available(ollama_url):
                raise ValueError(
                    f"Ollama server not available at {ollama_url}. Please ensure Ollama is running."
                )

            # Initialize Ollama LLM
            llm = OllamaLLM(
                model=model_name, temperature=temperature, base_url=ollama_url
            )

            # Store connection parameters for tool calls
            self.server_params = StdioServerParameters(
                command="python3",
                args=[os.path.join(os.path.dirname(__file__), "my_custom_tools.py")],
            )

            print("✅ MCP Agent initialized successfully!")
            print(f"🔧 Connected to Ollama server at: {ollama_url}")
            print(f"🤖 Using model: {model_name}")
            print(f"🔧 Connected to local MCP server at: {self.config_path}")

        except Exception as e:
            print(f"❌ Failed to initialize MCP Agent: {e}")
            raise

    def _check_ollama_available(self, ollama_url: str) -> bool:
        """Check if Ollama server is available and responsive."""
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    async def query(self, user_input: str) -> str:
        """Send a query to the agent and get a response."""
        if not self.agent:
            await self.initialize()

        try:
            response = await self.agent.run(user_input)
            return response
        except Exception as e:
            return f"Error processing query: {e}"

    async def interactive_mode(self):
        """Start interactive chat mode with the agent."""
        print("\n🤖 MCP Agent Interactive Mode")
        print("Type 'exit' or 'quit' to end the session")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                print("🤔 Thinking...")
                response = await self.query(user_input)
                print(f"\n🤖 Agent: {response}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def demo_queries(self):
        """Run some example queries to demonstrate functionality."""
        demo_queries = [
            "What's my overall table tennis win rate?",
            "How should I size my position if I have $10,000 and want to risk 2% on a $150 stock with stop loss at $145?",
            "What's my recent match history against John?",
            "Based on my 66.7% win rate, what trading position size would be appropriate for a moderate risk strategy?",
        ]

        print("\n🎯 Running Demo Queries")
        print("=" * 50)

        for i, query in enumerate(demo_queries, 1):
            print(f"\n--- Query {i}: {query} ---")
            try:
                response = await self.query(query)
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main function to run the MCP Agent client."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Agent Client")
    parser.add_argument("--config", type=str, help="Path to MCP config file")
    parser.add_argument(
        "--model", type=str, default="Nemotron-3-nano", help="Ollama model to use"
    )
    parser.add_argument("--demo", action="store_true", help="Run demo queries")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )
    parser.add_argument("--query", "-q", type=str, help="Single query to run")

    args = parser.parse_args()

    # Create agent instance
    agent = LocalMCPAgent(args.config)

    try:
        await agent.initialize(args.model)

        if args.demo:
            await agent.demo_queries()
        elif args.interactive:
            await agent.interactive_mode()
        elif args.query:
            response = await agent.query(args.query)
            print(f"\n🤖 Agent: {response}")
        else:
            print(
                "📖 Use --interactive for chat mode, --demo for examples, or --query for single question"
            )
            print("Example: python agent_client.py --interactive")
            print("Example: python agent_client.py --demo")
            print("Example: python agent_client.py --query 'What is my win rate?'")

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
