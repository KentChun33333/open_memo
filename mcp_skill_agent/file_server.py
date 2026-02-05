import asyncio
import os
import re
from pathlib import Path
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP
import logging
import json
import datetime
import traceback

# Setup robust logging that NEVER writes to stdout (which breaks MCP)
def setup_file_logging():
    try:
        # Determine log path: ../.agent/memory/observation/file_tools.log
        base_dir = Path(__file__).parent.parent.resolve()
        log_dir = base_dir / ".agent" / "memory" / "observation"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "file_tools_verbose.log"
        
        # Configure a specific logger for tools
        tool_logger = logging.getLogger("mcp_tools")
        tool_logger.setLevel(logging.DEBUG)
        
        # File Handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Remove existing handlers to avoid duplicates
        if tool_logger.hasHandlers():
            tool_logger.handlers.clear()
            
        tool_logger.addHandler(fh)
        tool_logger.propagate = False # Do not propagate to root (which might print to stderr/stdout)
        
        return tool_logger
    except Exception as e:
        # If logging setup fails, purely silent fallback (to protect stdout)
        return logging.getLogger("null")

tool_logger = setup_file_logging()

import functools

# ... (logging setup) ...

def log_activity(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        tool_logger.info(f"======== TOOL CALL: {func_name} ========")
        tool_logger.info(f"INPUT Args: {args}")
        tool_logger.info(f"INPUT Kwargs: {kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            
            # Truncate result for log if massive, but keep it generous as requested
            log_res = str(result)
            if len(log_res) > 20000:
                log_res = log_res[:20000] + "... [truncated]"
            
            tool_logger.info(f"OUTPUT: {log_res}")
            tool_logger.info(f"======== END TOOL: {func_name} ========\n")
            return result
        except Exception as e:
            tool_logger.error(f"ERROR in {func_name}: {e}\n{traceback.format_exc()}")
            tool_logger.info(f"======== END TOOL (ERROR): {func_name} ========\n")
            raise e
            
    return wrapper

# Initialize FastMCP server instance
mcp = FastMCP("file-tools")

#
# Tools referenced from nanobot/agent/tools/filesystem.py
#

@mcp.tool()
@log_activity
async def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    try:
        file_path = Path(path).expanduser()
        if not file_path.exists():
            return f"Error: File not found: {path}"
        if not file_path.is_file():
            return f"Error: Not a file: {path}"
        
        content = file_path.read_text(encoding="utf-8")
        return content
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
@log_activity
async def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path. Creates parent directories if needed."""
    try:
        file_path = Path(path).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} bytes to {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
@log_activity
async def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Edit a file by replacing old_text with new_text. The old_text must exist exactly in the file."""
    try:
        file_path = Path(path).expanduser()
        if not file_path.exists():
            return f"Error: File not found: {path}"
        
        content = file_path.read_text(encoding="utf-8")
        
        if old_text not in content:
            return f"Error: old_text not found in file. Make sure it matches exactly."
        
        # Count occurrences
        count = content.count(old_text)
        if count > 1:
            return f"Warning: old_text appears {count} times. Please provide more context to make it unique."
        
        new_content = content.replace(old_text, new_text, 1)
        file_path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully edited {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"

@mcp.tool()
@log_activity
async def list_dir(path: str) -> str:
    """List the contents of a directory."""
    try:
        dir_path = Path(path).expanduser()
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"
        if not dir_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        items = []
        for item in sorted(dir_path.iterdir()):
            prefix = "📁 " if item.is_dir() else "📄 "
            items.append(f"{prefix}{item.name}")
        
        if not items:
            return f"Directory {path} is empty"
        
        return "\n".join(items)
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

#
# Tools referenced from nanobot/agent/tools/shell.py
#

def _guard_command(command: str, cwd: str) -> str | None:
    """Best-effort safety guard for potentially destructive commands."""
    
    # Constants from nanobot/agent/tools/shell.py
    deny_patterns = [
        r"\brm\s+-[rf]{1,2}\b",          # rm -r, rm -rf, rm -fr
        r"\bdel\s+/[fq]\b",              # del /f, del /q
        r"\brmdir\s+/s\b",               # rmdir /s
        r"\b(format|mkfs|diskpart)\b",   # disk operations
        r"\bdd\s+if=",                   # dd
        r">\s*/dev/sd",                  # write to disk
        r"\b(shutdown|reboot|poweroff)\b",  # system power
        r":\(\)\s*\{.*\};\s*:",          # fork bomb
    ]
    # In nanobot, allow_patterns defaults to [] and restrict_to_workspace to False (by default config)
    # enforcing restrict_to_workspace = False as per default unless we want to enforce it.
    # The nanobot implementation passed these into __init__. 
    # Here we hardcode the defaults or "safe" values. 
    # Let's stick to the default ExecTool behavior:
    # timeout=60, restrict_to_workspace=False (unless we want to be safer)
    
    allow_patterns = []
    restrict_to_workspace = False

    cmd = command.strip()
    lower = cmd.lower()

    for pattern in deny_patterns:
        if re.search(pattern, lower):
            return "Error: Command blocked by safety guard (dangerous pattern detected)"

    if allow_patterns:
        if not any(re.search(p, lower) for p in allow_patterns):
            return "Error: Command blocked by safety guard (not in allowlist)"

    if restrict_to_workspace:
        if "..\\" in cmd or "../" in cmd:
            return "Error: Command blocked by safety guard (path traversal detected)"

        cwd_path = Path(cwd).resolve()

        win_paths = re.findall(r"[A-Za-z]:\\[^\\\"']+", cmd)
        posix_paths = re.findall(r"/[^\s\"']+", cmd)

        for raw in win_paths + posix_paths:
            try:
                p = Path(raw).resolve()
            except Exception:
                continue
            if cwd_path not in p.parents and p != cwd_path:
                return "Error: Command blocked by safety guard (path outside working dir)"

    return None

@mcp.tool()
@log_activity
async def execute_command(command: str, working_dir: Optional[str] = None) -> str:
    """Execute a shell command and return its output. Use with caution."""
    # Logic from nanobot ExecTool.execute
    cwd = working_dir or os.getcwd()
    guard_error = _guard_command(command, cwd)
    if guard_error:
        return guard_error
    
    try:
        timeout = 60  # Default from nanobot
        
        # Extra logging for command execution start
        tool_logger.info(f"EXEC SHELL: '{command}' in '{cwd}'")

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            return f"Error: Command timed out after {timeout} seconds"
        
        output_parts = []
        
        if stdout:
            output_parts.append(stdout.decode("utf-8", errors="replace"))
        
        if stderr:
            stderr_text = stderr.decode("utf-8", errors="replace")
            if stderr_text.strip():
                output_parts.append(f"STDERR:\n{stderr_text}")
        
        if process.returncode != 0:
            output_parts.append(f"\nExit code: {process.returncode}")
        
        result = "\n".join(output_parts) if output_parts else "(no output)"
        
        # Truncate very long output
        max_len = 10000
        if len(result) > max_len:
            result = result[:max_len] + f"\n... (truncated, {len(result) - max_len} more chars)"
        
        return result
        
    except Exception as e:
        return f"Error executing command: {str(e)}"

if __name__ == "__main__":
    try:
        tool_logger.info("Starting file-tools MCP server...")
        mcp.run()
    except Exception as e:
        tool_logger.critical(f"SERVER CRASH: {e}", exc_info=True)
        raise e
