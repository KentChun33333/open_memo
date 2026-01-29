from mcp.server import FastMCP
from typing import List, Dict
import json
import os

# Initialize Server
mcp = FastMCP("Memo-Server")

# In-Memory Store (Could be persisted to JSON if needed)
# Structure: [{"step_id": 1, "message": "...", "stdout": "...", "timestamp": ...}]
HISTORY: List[Dict] = []

@mcp.tool()
def log_step(step_id: str, message: str, stdout: str = "") -> str:
    """Logs the execution result of a step.
    
    Args:
        step_id: The ID of the step (e.g., "1", "1.1").
        message: A summary of what was done or found.
        stdout: The raw output from any commands executed (optional).
    """
    entry = {
        "step_id": step_id,
        "message": message,
        "stdout": stdout
    }
    HISTORY.append(entry)
    return f"Logged Step {step_id}: {message[:50]}..."

@mcp.tool()
def read_history(limit: int = 5) -> str:
    """Reads the execution history of previous steps.
    
    Args:
        limit: Number of recent steps to retrieve (default: 5).
    """
    if not HISTORY:
        return "No history yet."
    
    # Get last N entries
    recent = HISTORY[-limit:]
    output = "--- EXECUTION HISTORY ---\n"
    
    for entry in recent:
        output += f"Step {entry['step_id']}:\n"
        output += f"Message: {entry['message']}\n"
        if entry['stdout']:
            output += f"Output: {entry['stdout'][:500]}...\n" # Truncate long logs
        output += "-"*20 + "\n"
        
    return output

@mcp.tool()
def clear_history() -> str:
    """Clears the session history."""
    HISTORY.clear()
    return "History cleared."

if __name__ == "__main__":
    mcp.run(transport="stdio")
