import os
import logging
from mcp.server.fastmcp import FastMCP
from typing import Literal, Optional, List, Union
from pathlib import Path
# Initialize FastMCP server instance shared by all modules
mcp = FastMCP("file-tools")
logger = logging.getLogger(__name__)

# Constants
SNIPPET_LINES: int = 4
MAX_RESPONSE_LEN: int = 16000
TRUNCATED_MESSAGE: str = (
    "<response clipped><NOTE>To save on context only part of this file has been shown to you. "
    "You should retry this tool after you have searched inside the file with `grep -n` "
    "in order to find the line numbers of what you are looking for.</NOTE>"
)

# In-memory history for undo functionality
# Dictionary mapping path -> list of previous content versions
_file_history = {}

Command = Literal[
    "view",
    "create",
    "str_replace",
    "insert",
    "undo_edit",
]

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
    """Writes content to a file or artifacts or code asset at the given path. Overwrites if exists."""
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
        files = glob.glob('**/*', recursive=True)
        output = f"Contents of {path} (recursive):\n"
        for f in files:
            output += f"{f}\n"
            
        return output
    except Exception as e:
        logger.error(f"Error listing directory: {str(e)}")
        return f"Error listing directory: {str(e)}"


def maybe_truncate(
    content: str, truncate_after: Optional[int] = MAX_RESPONSE_LEN
) -> str:
    """Truncate content and append a notice if content exceeds the specified length."""
    if not truncate_after or len(content) <= truncate_after:
        return content
    return content[:truncate_after] + TRUNCATED_MESSAGE

def _make_output(
    file_content: str,
    file_descriptor: str,
    init_line: int = 1,
    expand_tabs: bool = True,
) -> str:
    """Format file content for display with line numbers."""
    file_content = maybe_truncate(file_content)
    if expand_tabs:
        file_content = file_content.expandtabs()

    # Add line numbers to each line
    file_content = "\n".join(
        [
            f"{i + init_line:6}\t{line}"
            for i, line in enumerate(file_content.split("\n"))
        ]
    )

    return (
        f"Here's the result of running `cat -n` on {file_descriptor}:\n"
        + file_content
        + "\n"
    )

@mcp.tool()
def str_replace_editor(
    command: str,
    path: str,
    file_text: Optional[str] = None,
    view_range: Optional[List[int]] = None,
    old_str: Optional[str] = None,
    new_str: Optional[str] = None,
    insert_line: Optional[int] = None,
) -> str:
    """
    Custom editing tool for viewing, creating and editing files
    * State is persistent across command calls and discussions with the user
    * If `path` is a file, `view` displays the result of applying `cat -n`. If `path` is a directory, `view` lists non-hidden files and directories up to 2 levels deep
    * The `create` command cannot be used if the specified `path` already exists as a file
    * If a `command` generates a long output, it will be truncated and marked with `<response clipped>`
    * The `undo_edit` command will revert the last edit made to the file at `path`

    Notes for using the `str_replace` command:
    * The `old_str` parameter should match EXACTLY one or more consecutive lines from the original file. Be mindful of whitespaces!
    * If the `old_str` parameter is not unique in the file, the replacement will not be performed. Make sure to include enough context in `old_str` to make it unique
    * The `new_str` parameter should contain the edited lines that should replace the `old_str`
    """
    global _file_history
    
    logger.info(f"str_replace_editor command={command} path={path}")
    
    # Path validation
    p = Path(path).resolve()
    
    if command == "view":
        return _view(p, view_range)
    elif command == "create":
        return _create(p, file_text)
    elif command == "str_replace":
        return _str_replace(p, old_str, new_str)
    elif command == "insert":
        return _insert(p, insert_line, new_str)
    elif command == "undo_edit":
        return _undo_edit(p)
    else:
        return f"Error: Unrecognized command {command}. Allowed: view, create, str_replace, insert, undo_edit"

def _view(path: Path, view_range: Optional[List[int]] = None) -> str:
    if not path.exists():
        return f"Error: The path {path} does not exist."
    
    if path.is_dir():
        if view_range:
            return "Error: The `view_range` parameter is not allowed when `path` points to a directory."
        
        # Simple tree view
        # We can reuse the list_directory logic or just implement a simple find command
        # Let's use os.walk slightly modified for depth 2
        root_str = str(path)
        output = []
        try:
            cmd = f"find {root_str} -maxdepth 2 -not -path '*/.*'"
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error listing directory: {result.stderr}"
            return f"Files in {path}:\n{result.stdout}"
        except Exception as e:
            return f"Error viewing directory: {str(e)}"

    # File viewing
    try:
        content = path.read_text(encoding="utf-8")
        init_line = 1
        
        if view_range:
            if len(view_range) != 2:
                return "Error: Invalid `view_range`. It should be a list of two integers."
            
            lines = content.split("\n")
            n_lines = len(lines)
            start, end = view_range
            
            if start < 1 or start > n_lines:
                return f"Error: Invalid `view_range`. Start line {start} out of bounds [1, {n_lines}]"
            
            if end != -1 and end < start:
                return f"Error: Invalid `view_range`. End line {end} < Start line {start}"
                
            init_line = start
            if end == -1:
                content = "\n".join(lines[start-1:])
            else:
                content = "\n".join(lines[start-1:end])
                
        return _make_output(content, str(path), init_line)
        
    except Exception as e:
        return f"Error reading file: {str(e)}"

def _create(path: Path, file_text: Optional[str]) -> str:
    if file_text is None:
        return "Error: Parameter `file_text` is required for command: create"
    
    if path.exists():
        # OpenManus prevents overwrite on create.
        return f"Error: File already exists at: {path}. Cannot overwrite files using command `create`."
        
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_text, encoding="utf-8")
        
        # Init history
        if path not in _file_history:
            _file_history[path] = []
        _file_history[path].append(file_text)
        
        return f"File created successfully at: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def _str_replace(path: Path, old_str: Optional[str], new_str: Optional[str]) -> str:
    if old_str is None:
        return "Error: Parameter `old_str` is required for command: str_replace"
    if not path.exists():
        return f"Error: Path {path} does not exist"
        
    try:
        content = path.read_text(encoding="utf-8").expandtabs()
        old_str = old_str.expandtabs()
        new_str = new_str.expandtabs() if new_str is not None else ""
        
        occurrences = content.count(old_str)
        if occurrences == 0:
            return f"Error: old_str `{old_str}` did not appear verbatim in {path}."
        if occurrences > 1:
            return f"Error: Multiple occurrences ({occurrences}) of old_str found. Please ensure it is unique."
            
        new_content = content.replace(old_str, new_str)
        
        # Save history
        if path not in _file_history:
            _file_history[path] = []
        _file_history[path].append(content)
        
        path.write_text(new_content, encoding="utf-8")
        
        # Create snippet
        # Logic to show context around change
        replacement_line = content.split(old_str)[0].count("\n")
        start_line = max(0, replacement_line - SNIPPET_LINES)
        end_line = replacement_line + SNIPPET_LINES + new_str.count("\n")
        snippet = "\n".join(new_content.split("\n")[start_line : end_line + 1])

        success_msg = f"The file {path} has been edited. "
        success_msg += _make_output(
            snippet, f"a snippet of {path}", start_line + 1
        )
        success_msg += "Review the changes and make sure they are as expected."
        return success_msg
        
    except Exception as e:
        return f"Error modifying file: {str(e)}"

def _insert(path: Path, insert_line: Optional[int], new_str: Optional[str]) -> str:
    if insert_line is None:
        return "Error: Parameter `insert_line` is required for command: insert"
    if new_str is None:
        return "Error: Parameter `new_str` is required for command: insert"
    if not path.exists():
        return f"Error: Path {path} does not exist"

    try:
        content = path.read_text(encoding="utf-8").expandtabs()
        new_str = new_str.expandtabs()
        lines = content.split("\n")
        n_lines = len(lines)
        
        if insert_line < 0 or insert_line > n_lines:
            return f"Error: Invalid `insert_line` {insert_line}. Range: [0, {n_lines}]"
            
        new_lines = new_str.split("\n")
        final_lines = lines[:insert_line] + new_lines + lines[insert_line:]
        
        # Save history
        if path not in _file_history:
            _file_history[path] = []
        _file_history[path].append(content)
        
        new_content = "\n".join(final_lines)
        path.write_text(new_content, encoding="utf-8")
        
        # Snippet
        snippet_lines = (
            lines[max(0, insert_line - SNIPPET_LINES) : insert_line]
            + new_lines
            + lines[insert_line : insert_line + SNIPPET_LINES]
        )
        snippet = "\n".join(snippet_lines)
        
        success_msg = f"The file {path} has been edited. "
        success_msg += _make_output(
            snippet,
            "a snippet of the edited file",
            max(1, insert_line - SNIPPET_LINES + 1),
        )
        return success_msg
        
    except Exception as e:
        return f"Error inserting into file: {str(e)}"

def _undo_edit(path: Path) -> str:
    if path not in _file_history or not _file_history[path]:
        return f"Error: No edit history found for {path}."
        
    try:
        old_text = _file_history[path].pop()
        path.write_text(old_text, encoding="utf-8")
        
        return f"Last edit to {path} undone successfully.\n{_make_output(old_text, str(path))}"
    except Exception as e:
        return f"Error undoing edit: {str(e)}"


if __name__ == "__main__":
    mcp.run()
