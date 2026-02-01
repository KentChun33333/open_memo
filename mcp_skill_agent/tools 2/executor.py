import asyncio
import os
import signal
from typing import Optional
from .core import mcp

# Sentinel to detect end of command output
SENTINEL = "<<CMD_END_SENTINEL>>"
DEFAULT_TIMEOUT = 120.0

class BashSession:
    _instance = None
    
    def __init__(self):
        self._process: Optional[asyncio.subprocess.Process] = None
        self._started = False
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    async def start(self):
        if self._started and self._process and self._process.returncode is None:
            return

        self._process = await asyncio.create_subprocess_shell(
            "/bin/bash",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            preexec_fn=os.setsid,  # Create new session group
            shell=True,
            bufsize=0
        )
        self._started = True
        
    async def restart(self):
        if self._process:
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            except:
                pass
        self._started = False
        await self.start()

    async def run(self, command: str, timeout: float = DEFAULT_TIMEOUT) -> str:
        if not self._started or not self._process:
            await self.start()
            
        if self._process.returncode is not None:
            await self.restart()

        assert self._process.stdin
        assert self._process.stdout
        assert self._process.stderr

        # Write command + echo sentinel + echo exit code
        # We also capture exit code to report success/failure
        # Logic: 
        # 1. run command
        # 2. echo SENTINEL
        
        full_cmd = f"{command}; echo '{SENTINEL}'\n"
        self._process.stdin.write(full_cmd.encode())
        await self._process.stdin.drain()
        
        output_buffer = []
        
        try:
            async with asyncio.timeout(timeout):
                while True:
                    # Read line by line? Or chunk?
                    # readline is safer for seeing the sentinel line
                    line = await self._process.stdout.readline()
                    decoded_line = line.decode()
                    
                    if SENTINEL in decoded_line:
                        # We found the sentinel
                        # Remove it if it's mixed with other output (unlikely with readline but possible)
                        pre_sentinel = decoded_line.split(SENTINEL)[0]
                        if pre_sentinel.strip():
                            output_buffer.append(pre_sentinel)
                        break
                        
                    output_buffer.append(decoded_line)
                    
                    # Also check stderr - problem is readline blocks.
                    # Ideally we should read stdout/stderr concurrently. 
                    # For simplicity in this lightweight agent, we might merge stderr to stdout via redirect in the shell command?
                    # Actually, combining streams is easier: "cmd 2>&1"
                    
        except asyncio.TimeoutError:
            # kill process and restart
            await self.restart()
            return f"Error: Command timed out after {timeout} seconds. Session restarted."
            
        return "".join(output_buffer).strip()

# Global session
session = BashSession()

@mcp.tool()
async def run_bash_command(command: str, timeout: int = 120, restart: bool = False) -> str:
    """
    Execute a bash command in a persistent session.
    State (directory, variables) is preserved between calls.
    
    Args:
        command: The bash command to execute.
        timeout: Timeout in seconds (default 120).
        restart: If True, restart the session before running.
    """
    # Note: We merge stderr to stdout to simplify capture
    cmd_with_stderr = f"{{ {command} ; }} 2>&1"
    
    if restart:
        await session.restart()
        return "Session restarted."
        
    return await session.run(cmd_with_stderr, timeout=float(timeout))
