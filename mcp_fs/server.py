from fastmcp import FastMCP
import os
import datetime

# Initialize the server
mcp = FastMCP("Filesystem-Server")

@mcp.tool()
def read_file(path: str) -> str:
    """Reads the content of a file at the given path."""
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the given path. Overwrites if exists."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_directory(path: str = ".") -> str:
    """Lists files and directories in the given path."""
    try:
        if not os.path.exists(path):
            return f"Error: Path not found at {path}"
        
        items = os.listdir(path)
        output = f"Contents of {os.path.abspath(path)}:\n"
        
        for item in items:
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            prefix = "[DIR] " if is_dir else "[FILE]"
            output += f"{prefix} {item}\n"
            
        return output
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def file_info(path: str) -> str:
    """Returns metadata about a file."""
    try:
        if not os.path.exists(path):
            return f"Error: Path not found at {path}"
            
        stats = os.stat(path)
        info = f"File Info for: {path}\n"
        info += f"Size: {stats.st_size} bytes\n"
        info += f"Created: {datetime.datetime.fromtimestamp(stats.st_ctime)}\n"
        info += f"Modified: {datetime.datetime.fromtimestamp(stats.st_mtime)}\n"
        info += f"Is Directory: {os.path.isdir(path)}\n"
        
        return info
    except Exception as e:
        return f"Error getting file info: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
