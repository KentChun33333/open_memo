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
def list_directory(path: str = ".") -> str:
    """Lists directory tree from the given path."""
    logger.info(f"Listing directory tree: {path}")
    
    def _generate_tree(dir_path: str, prefix: str = "") -> str:
        output = ""
        try:
            items = sorted([i for i in os.listdir(dir_path) if not (i.startswith(".") and i != ".")])
        except OSError:
            return ""
        
        pointers = [("├── ", "│   ")] * (len(items) - 1) + [("└── ", "    ")] if items else []

        for i, item in enumerate(items):
            pointer, extension = pointers[i]
            full_path = os.path.join(dir_path, item)
            output += f"{prefix}{pointer}{item}\n"
            
            if os.path.isdir(full_path):
                 output += _generate_tree(full_path, prefix + extension)
        return output

    try:
        if not os.path.exists(path):
            logger.error(f"Error: Path not found at {path}")
            return f"Error: Path not found at {path}"
        
        output = f"Contents of {path}:\n"
        output += _generate_tree(path)
        return output
    except Exception as e:
        logger.error(f"Error listing directory: {str(e)}")
        return f"Error listing directory: {str(e)}"
