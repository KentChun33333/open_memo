# Personal MCP Server - Trading & Table Tennis Stats

A self-hosted MCP (Model Context Protocol) server that provides custom tools for financial calculations and local table tennis match history retrieval.

## 🚀 Features

### Financial Tools
- **Position Size Calculator**: Calculate optimal trade sizes based on risk management principles

### Table Tennis Stats
- **Match History**: Retrieve recent matches against specific opponents
- **Overall Statistics**: Get win/loss records and performance metrics
- **Data Resources**: Read-only access to match data for context

## 📋 Prerequisites

- Python 3.8+
- Node.js (for MCP Inspector testing)
- uv (recommended Python package manager) or pip
- **Ollama**: Install and run Ollama locally (https://ollama.ai)
- **Nemotron-3-nano**: Pull the model with `ollama pull nemotron-3-nano`

## 🛠️ Installation

1. **Clone/Download this project** to your local directory

2. **Install dependencies**:
   ```bash
   # Using uv (recommended for faster startup)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   
   # Or using pip
   pip install -r requirements.txt
   ```

## 🎯 Available Tools

### 1. calculate_position_size
Calculate position sizing for trades based on risk parameters.

**Parameters:**
- `account_value` (float): Total account value in USD
- `risk_percent` (float): Percentage of account to risk (e.g., 2.0 for 2%)
- `entry_price` (float): Entry price per share/contract
- `stop_loss` (float): Stop loss price per share/contract

**Example:**
```python
calculate_position_size(10000, 2.0, 150.0, 145.0)
# Returns: "Risking $200.00: Buy 40 units at $150.00 with stop loss at $145.00."
```

### 2. get_match_history
Retrieve recent match results against a specific opponent.

**Parameters:**
- `player_name` (str): Name of the opponent to search for

**Example:**
```python
get_match_history("John")
# Returns: Recent matches against John:
# - 2024-02-16: Win (11-8, 11-6, 11-7)
# - 2024-02-05: Loss (9-11, 10-12, 8-11)
# - 2024-01-26: Win (11-9, 11-7, 11-8)
```

### 3. get_match_stats
Get overall match statistics and performance metrics.

**Returns:**
```python
get_match_stats()
# Returns: Overall Statistics:
# Total Matches: 15
# Wins: 10
# Losses: 5
# Win Rate: 66.7%
# Last 10 Matches Win Rate: 70.0%
```

## 🔧 Configuration

### MCP Server Registration

The `mcp-config.json` file is already configured for your local server:

```json
{
  "mcpServers": {
    "my-local-tools": {
      "command": "python3",
      "args": ["/Users/kentchiu/Documents/Github/new-openc/mcp-server/my_custom_tools.py"]
    }
  }
}
```

**Important**: Update the absolute path to match your system if you move the project.

### Environment Configuration

Copy and configure your environment:
```bash
cp .env.example .env
# Edit .env with your Ollama configuration
```

Required environment variables:
- `OLLAMA_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model name (default: Nemotron-3-nano)
- `MCP_SERVER_PATH`: Path to your MCP server (optional, defaults to local)

## 🧪 Testing with MCP Inspector

Test your tools before connecting to your agent:

```bash
npx @modelcontextprotocol/inspector python3 my_custom_tools.py
```

This opens a web interface where you can manually test each tool.

## 📊 Data Structure

The `matches.csv` file follows this format:

```csv
date,opponent,result,score
2024-01-05,John,W,"11-7, 11-9, 11-6"
2024-01-08,Mike,L,"9-11, 8-11, 11-9, 8-11"
```

- `date`: Match date (YYYY-MM-DD)
- `opponent`: Opponent's name
- `result`: W (Win) or L (Loss)
- `score`: Game scores as quoted string (handles variable game counts)

**Sample data included**: The project comes with 15 sample matches across 4 opponents (John, Mike, Sarah, Emma) demonstrating win/loss patterns.

## 🚀 Running the Server

### Direct Execution
```bash
python3 my_custom_tools.py
```

### With uv (faster startup)
```bash
uv run my_custom_tools.py
```

## 🤖 MCP Agent Integration

### Quick Start
```bash
# 1. Install dependencies and setup
pip install -r requirements.txt
python3 setup.py

# 2. Start Ollama (if not already running)
ollama serve

# 3. Verify Nemotron-3-nano is available
ollama list  # Should show nemotron-3-nano

# 4. Test the agent
python3 agent_client.py --demo

# 5. Interactive mode
python3 agent_client.py --interactive
```

### Available Commands
```bash
# Agent client with different modes
python3 agent_client.py --interactive     # Interactive chat mode
python3 agent_client.py --demo           # Run demo queries
python3 agent_client.py --query "What's my win rate?"  # Single query
python3 agent_client.py --model Nemotron-3-nano  # Specify model

# Example scenarios
python3 examples.py --scenario 1          # Trading analysis
python3 examples.py --scenario 2          # Sports statistics  
python3 examples.py --scenario 3          # Combined insights
python3 examples.py --scenario 4          # Risk management
python3 examples.py --all                 # Run all scenarios
python3 examples.py --interactive         # Interactive exploration
```

### Sample Agent Conversations

**Trading Analysis:**
- *"I have $25,000 in my account. If I want to risk 2% on a trade with entry at $200 and stop loss at $190, how many shares should I buy?"*

**Sports Statistics:**
- *"What's my overall win rate and match statistics?"*
- *"Show me my recent match history against John"*

**Combined Insights:**
- *"Based on my 66.7% overall win rate, what would be an appropriate position sizing strategy for moderate risk?"*
- *"Given my recent 10-match win rate of 70%, should I take more aggressive trading positions?"*

**Risk Management:**
- *"Calculate position sizes for different risk levels (1%, 2%, 3%) for a $30,000 account on a $100 stock with stop at $95"*
- *"If I'm on a 3-game winning streak in table tennis, how might this confidence affect my trading psychology?"*

## 🛠️ Customization

### Adding New Tools

Add new tools by creating functions with the `@mcp.tool()` decorator:

```python
@mcp.tool()
def your_custom_function(param1: str, param2: int) -> str:
    """Description of what your function does."""
    # Your logic here
    return "Result as string"
```

### Adding Resources

Provide read-only data access with `@mcp.resource()`:

```python
@mcp.resource("data://your-resource")
def your_resource():
    """Provides read-only access to your data."""
    return "Your data content"
```

### Extending the Agent

Add custom prompts and scenarios in `examples.py`:
```python
async def scenario_5_custom():
    """Your custom analysis scenario."""
    agent = LocalMCPAgent()
    await agent.initialize()
    
    query = "Your specific domain query here"
    response = await agent.query(query)
    print(f"Response: {response}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Import errors**: Ensure you've installed the requirements with `pip install -r requirements.txt`
2. **File not found**: Make sure `matches.csv` is in the same directory as the script
3. **Path issues**: Update the absolute path in `mcp-config.json` to match your system
4. **Permission issues**: Ensure Python can read/write in the directory
5. **OpenAI API key**: Set your API key in `.env` file or as environment variable
6. **MCP Agent errors**: Ensure your MCP server is running when testing the agent

### Debug Mode

Add logging to troubleshoot:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Components

Test each component separately:
```bash
# Test MCP server tools
python3 -c "import pandas as pd; print(pd.read_csv('matches.csv'))"

# Test agent setup
python3 setup.py

# Test individual scenarios
python3 examples.py --scenario 1
```

## 📈 Performance Tips

1. **Use uv**: Faster Python package management and startup
2. **Optimize data**: Keep CSV files small for faster processing
3. **Cache results**: Consider adding caching for frequently accessed data

## 📁 Project Structure

```
mcp-server/
├── my_custom_tools.py      # FastMCP server with 3 tools + 1 resource
├── matches.csv           # Sample table tennis data (15 matches)
├── agent_client.py       # MCP Agent client for OpenAI integration
├── examples.py           # 4 demo scenarios + interactive mode
├── setup.py             # Automated setup and testing script
├── requirements.txt     # Python dependencies
├── mcp-config.json     # MCP server configuration
├── .env.example        # Environment variables template
└── README.md           # This documentation
```

## 🚀 Quick Setup Guide

1. **Clone/Download** this project to your local directory
2. **Run setup**: `python3 setup.py`
3. **Configure API key**: Edit `.env` with your OpenAI API key
4. **Test**: `python3 agent_client.py --demo`
5. **Use**: `python3 agent_client.py --interactive`

## 🤝 Contributing

1. Add new tools following the existing pattern in `my_custom_tools.py`
2. Update this README for new functionality
3. Add scenarios to `examples.py` for new functionality
4. Test with MCP Inspector: `npx @modelcontextprotocol/inspector python3 my_custom_tools.py`

## 📄 License

This project is open source and available under the MIT License.