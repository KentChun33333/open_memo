import os
from .core import mcp

# We'll use a simple in-memory state, similar to the original meta-server,
# but we could easily back this with a file if needed.
session_state = {
    "tasks": [],
    "artifacts_dir": os.path.join(os.getcwd(), "artifacts")
}

@mcp.tool()
def create_task_list(tasks: list[str]) -> str:
    """
    Initialize the session with a list of high-level tasks.
    
    Args:
        tasks: A list of strings, each describing a task.
    
    Returns:
        A formatted string showing the created task list with IDs.
    """
    session_state["tasks"] = []
    output = ["Task List Created:"]
    
    for i, task_desc in enumerate(tasks):
        task = {
            "id": i + 1,
            "description": task_desc,
            "status": "pending",
            "summary": ""
        }
        session_state["tasks"].append(task)
        output.append(f"{task['id']}. [ ] {task['description']}")
        
    return "\n".join(output)

@mcp.tool()
def update_task(task_id: int, status: str, summary: str = "") -> str:
    """
    Update the status and summary of a specific task.
    
    Args:
        task_id: The ID of the task to update (1-based).
        status: The new status ('pending', 'in-progress', 'done', 'failed').
        summary: Optional summary of what was accomplished.
        
    Returns:
        Confirmation message and current task list.
    """
    task = next((t for t in session_state["tasks"] if t["id"] == task_id), None)
    if not task:
        return f"Error: Task ID {task_id} not found."
    
    task["status"] = status
    if summary:
        task["summary"] = summary
        
    return get_task_status()

@mcp.tool()
def get_task_status() -> str:
    """
    Get the current status of all tasks.
    
    Returns:
        A formatted string showing the task list, statuses, and summaries.
    """
    if not session_state["tasks"]:
        return "No tasks defined. Use `create_task_list` first."
        
    output = ["Current Task Status:"]
    all_done = True
    
    for task in session_state["tasks"]:
        status_symbol = "[ ]"
        if task["status"] == "in-progress":
            status_symbol = "[/]"
            all_done = False
        elif task["status"] == "done":
            status_symbol = "[x]"
        elif task["status"] == "failed":
            status_symbol = "[!]"
            all_done = False
        else:
            all_done = False
            
        line = f"{task['id']}. {status_symbol} {task['description']} ({task['status']})"
        output.append(line)
        if task["summary"]:
            output.append(f"   Summary: {task['summary']}")
            
    if all_done:
        output.append("\nAll tasks completed! You may now use `notify_user` to finish.")
        
    return "\n".join(output)

@mcp.tool()
def notify_user(message: str) -> str:
    """
    Send a final notification to the user.
    """
    # Simply return the message as tool output for the agent to see.
    return f"Notification sent: {message}"
