# Install first: pip install mcp fastmcp
from fastmcp import FastMCP
import pandas as pd
import os

# Initialize the server
mcp = FastMCP("Personal-Trade-Server")


# TOOL 1: Financial Logic
@mcp.tool()
def calculate_position_size(
    account_value: float, risk_percent: float, entry_price: float, stop_loss: float
) -> str:
    """Calculates the number of shares/contracts to buy based on risk."""
    risk_amount = account_value * (risk_percent / 100)
    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share == 0:
        return "Error: Entry price and stop loss cannot be the same."
    position_size = risk_amount / risk_per_share
    return f"Risking ${risk_amount:.2f}: Buy {int(position_size)} units at ${entry_price:.2f} with stop loss at ${stop_loss:.2f}."


# TOOL 2: Local Data Access (e.g., your Table Tennis stats)
@mcp.tool()
def get_match_history(player_name: str) -> str:
    """Retrieves recent table tennis match results from a local CSV."""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "matches.csv")

        # Assuming you have a file 'matches.csv' in the same folder
        df = pd.read_csv(csv_path)

        # Filter by opponent name
        results = df[df["opponent"] == player_name].tail(3)

        if results.empty:
            return f"No matches found against player '{player_name}'."

        # Convert to readable format
        output = f"Recent matches against {player_name}:\n"
        for _, row in results.iterrows():
            result = "Win" if row["result"] == "W" else "Loss"
            output += f"- {row['date']}: {result} ({row['score']})\n"

        return output.strip()
    except FileNotFoundError:
        return f"Error: matches.csv file not found. Please create it in the same directory as this script."
    except Exception as e:
        return f"Error reading local data: {str(e)}"


# TOOL 3: Get all match statistics
@mcp.tool()
def get_match_stats() -> str:
    """Returns overall match statistics from the local CSV."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "matches.csv")

        df = pd.read_csv(csv_path)

        total_matches = len(df)
        wins = len(df[df["result"] == "W"])
        losses = len(df[df["result"] == "L"])
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        stats = f"Overall Statistics:\n"
        stats += f"Total Matches: {total_matches}\n"
        stats += f"Wins: {wins}\n"
        stats += f"Losses: {losses}\n"
        stats += f"Win Rate: {win_rate:.1f}%\n"

        # Recent performance (last 10 matches)
        recent = df.tail(10)
        recent_wins = len(recent[recent["result"] == "W"])
        recent_win_rate = (recent_wins / len(recent) * 100) if len(recent) > 0 else 0
        stats += f"Last 10 Matches Win Rate: {recent_win_rate:.1f}%"

        return stats
    except FileNotFoundError:
        return "Error: matches.csv file not found. Please create it in the same directory as this script."
    except Exception as e:
        return f"Error reading local data: {str(e)}"


# RESOURCE: Add match history as a read-only resource
@mcp.resource("matches://recent")
def get_recent_matches() -> str:
    """Provides read-only access to recent match history."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "matches.csv")

        df = pd.read_csv(csv_path)
        recent = df.tail(5).to_string(index=False)
        return f"Recent 5 matches:\n{recent}"
    except Exception as e:
        return f"Error reading match data: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
