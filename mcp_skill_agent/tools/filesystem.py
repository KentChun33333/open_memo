import os
import logging
from .core import mcp

logger = logging.getLogger(__name__)

@mcp.tool()
def read_file(path: str) -> str:
    """Reads the content of a file at the given path."""
    logger.info(f"Reading file: {path}")
    try:
        if not os.path.exists(path):
            logger.error(f"Error: File not found at {path}")
            return f"Error: File not found at {path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the given path. Overwrites if exists."""
    logger.info(f"Writing file to: {path}")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        logger.error(f"Error writing file: {str(e)}")
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_directory() -> str:
    """Lists all files under the current working directory using glob."""
    import glob
    path = os.getcwd()
    logger.info(f"Listing directory tree (glob): {path}")
    
    try:
        # Use glob to find all files recursively
        # recursive=True with '**' matches all files and directories
        # we can filter if needed, but 'all files' usually implies excluding directories or including them.
        # User requested 'list all files under current root', usually implies paths.
        
        files = glob.glob('**/*', recursive=True)
        
        # Filter out hidden files/dirs if desired, matching previous behavior
        # Previous behavior: if not (i.startswith(".") and i != ".")
        # Glob doesn't match dotfiles by default unless patterns start with dot.
        # '**/*' will not match .git/ etc usually.
        
        output = f"Contents of {path} (recursive):\n"
        for f in files:
            output += f"{f}\n"
            
        return output
    except Exception as e:
        logger.error(f"Error listing directory: {str(e)}")
        return f"Error listing directory: {str(e)}"
