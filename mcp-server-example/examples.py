#!/usr/bin/env python3
"""
Example usage scenarios for the MCP Agent with your trading and table tennis tools.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from agent_client import LocalMCPAgent


async def scenario_1_trading_analysis():
    """Scenario 1: Trading analysis with position sizing."""
    print("\n" + "=" * 60)
    print("🏦 SCENARIO 1: Trading Analysis")
    print("=" * 60)

    agent = LocalMCPAgent()
    await agent.initialize()

    queries = [
        "I have $25,000 in my account. If I want to risk 2% on a trade with entry at $200 and stop loss at $190, how many shares should I buy?",
        "Calculate position size for a $50,000 account, risking 1.5% on a stock at $75 with stop loss at $72.",
        "What's the risk amount for a $15,000 account with 3% risk on a trade?",
    ]

    for query in queries:
        print(f"\n📊 Query: {query}")
        response = await agent.query(query)
        print(f"💡 Response: {response}")


async def scenario_2_sports_statistics():
    """Scenario 2: Table tennis statistics and analysis."""
    print("\n" + "=" * 60)
    print("🏓 SCENARIO 2: Table Tennis Statistics")
    print("=" * 60)

    agent = LocalMCPAgent()
    await agent.initialize()

    queries = [
        "What's my overall win rate and match statistics?",
        "Show me my recent match history against John",
        "How have I been performing against Mike lately?",
        "What's my win rate in the last 10 matches?",
    ]

    for query in queries:
        print(f"\n🏓 Query: {query}")
        response = await agent.query(query)
        print(f"📈 Response: {response}")


async def scenario_3_combined_insights():
    """Scenario 3: Combined trading and sports insights."""
    print("\n" + "=" * 60)
    print("🎯 SCENARIO 3: Combined Analysis")
    print("=" * 60)

    agent = LocalMCPAgent()
    await agent.initialize()

    queries = [
        "Based on my 66.7% overall win rate, what would be an appropriate position sizing strategy for moderate risk?",
        "I've been playing well against John with 2 wins out of 3 matches. Given this confidence level, should I take a more aggressive position on my next trade?",
        "Analyze my recent performance trends and suggest trading risk levels that match my consistency",
        "My recent 10-match win rate is 70%. If I were to translate this confidence to trading, what position size would you recommend for a $20,000 account?",
    ]

    for query in queries:
        print(f"\n🎯 Query: {query}")
        response = await agent.query(query)
        print(f"🧠 Response: {response}")


async def scenario_4_risk_management():
    """Scenario 4: Advanced risk management scenarios."""
    print("\n" + "=" * 60)
    print("⚠️  SCENARIO 4: Risk Management")
    print("=" * 60)

    agent = LocalMCPAgent()
    await agent.initialize()

    queries = [
        "Calculate position sizes for different risk levels (1%, 2%, 3%) for a $30,000 account on a $100 stock with stop at $95",
        "Compare the risk/reward for my trading vs table tennis performance",
        "Given my inconsistent performance against Sarah (1 win, 2 losses), should I reduce my trading risk?",
        "If I'm on a 3-game winning streak in table tennis, how might this confidence affect my trading psychology and position sizing?",
    ]

    for query in queries:
        print(f"\n⚡ Query: {query}")
        response = await agent.query(query)
        print(f"🛡️  Response: {response}")


async def run_all_scenarios():
    """Run all example scenarios."""
    print("🚀 Running all MCP Agent scenarios...")
    print("Make sure your MCP server is running and OpenAI API key is set!")

    scenarios = [
        ("Trading Analysis", scenario_1_trading_analysis),
        ("Sports Statistics", scenario_2_sports_statistics),
        ("Combined Insights", scenario_3_combined_insights),
        ("Risk Management", scenario_4_risk_management),
    ]

    for name, scenario_func in scenarios:
        try:
            await scenario_func()
            print(f"\n✅ Completed: {name}")
        except Exception as e:
            print(f"\n❌ Failed: {name} - {e}")

    print("\n🎉 All scenarios completed!")


async def interactive_scenario():
    """Interactive scenario where user can choose what to explore."""
    print("\n" + "=" * 60)
    print("🎮 INTERACTIVE SCENARIO MODE")
    print("=" * 60)

    agent = LocalMCPAgent()
    await agent.initialize()

    suggested_queries = [
        "What are the key metrics from my trading and table tennis data?",
        "How does my competitive nature in sports translate to trading psychology?",
        "Create a risk management plan based on my performance consistency",
        "Compare my win rates across different opponents and suggest trading parallels",
    ]

    print("\n💡 Suggested queries:")
    for i, query in enumerate(suggested_queries, 1):
        print(f"{i}. {query}")

    print("\nType your own query or choose a number, 'exit' to quit")

    while True:
        try:
            user_input = input("\n🔍 Your query: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.isdigit() and 1 <= int(user_input) <= len(suggested_queries):
                query = suggested_queries[int(user_input) - 1]
                print(f"🎯 Selected: {query}")
            else:
                query = user_input

            print("🤔 Processing...")
            response = await agent.query(query)
            print(f"\n🤖 Agent Response:\n{response}\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main function to run examples."""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Agent Example Scenarios")
    parser.add_argument(
        "--scenario",
        "-s",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific scenario (1=Trading, 2=Sports, 3=Combined, 4=Risk)",
    )
    parser.add_argument("--all", "-a", action="store_true", help="Run all scenarios")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )

    args = parser.parse_args()

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable required!")
        print("📖 Set it in your .env file or export it:")
        print("export OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)

    if args.all:
        await run_all_scenarios()
    elif args.interactive:
        await interactive_scenario()
    elif args.scenario:
        scenarios = {
            1: scenario_1_trading_analysis,
            2: scenario_2_sports_statistics,
            3: scenario_3_combined_insights,
            4: scenario_4_risk_management,
        }
        await scenarios[args.scenario]()
    else:
        print("🎭 MCP Agent Example Scenarios")
        print("Choose an option:")
        print("  --scenario 1 : Trading Analysis")
        print("  --scenario 2 : Sports Statistics")
        print("  --scenario 3 : Combined Insights")
        print("  --scenario 4 : Risk Management")
        print("  --all        : Run all scenarios")
        print("  --interactive: Interactive exploration mode")
        print("\nExample: python examples.py --scenario 1")
        print("Example: python examples.py --all")
        print("Example: python examples.py --interactive")


if __name__ == "__main__":
    asyncio.run(main())
