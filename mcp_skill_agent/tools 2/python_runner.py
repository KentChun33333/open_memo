import multiprocessing
import sys
from io import StringIO
from typing import Dict
from .core import mcp

def _run_code(code: str, result_dict: dict, safe_globals: dict) -> None:
    original_stdout = sys.stdout
    try:
        output_buffer = StringIO()
        sys.stdout = output_buffer
        exec(code, safe_globals, safe_globals)
        result_dict["observation"] = output_buffer.getvalue()
        result_dict["success"] = True
    except Exception as e:
        result_dict["observation"] = str(e)
        result_dict["success"] = False
    finally:
        sys.stdout = original_stdout

@mcp.tool()
def run_python(code: str, timeout: int = 30) -> str:
    """
    Executes Python code in a separate process with timeout.
    
    Args:
        code: The Python code to execute.
        timeout: Execution timeout in seconds (default 30).
        
    Returns:
        The standard output of the code or error message.
    """
    with multiprocessing.Manager() as manager:
        result = manager.dict({"observation": "", "success": False})
        
        # Prepare globals
        # We can restrict builtins here if needed, but for a local agent we might want reasonable power.
        if isinstance(__builtins__, dict):
            safe_globals = {"__builtins__": __builtins__}
        else:
            safe_globals = {"__builtins__": __builtins__.__dict__.copy()}
            
        proc = multiprocessing.Process(
            target=_run_code, args=(code, result, safe_globals)
        )
        proc.start()
        proc.join(timeout)

        # Timeout handling
        if proc.is_alive():
            proc.terminate()
            proc.join(1)
            return f"Error: Execution timeout after {timeout} seconds"
            
        observation = result["observation"]
        success = result["success"]
        
        status = "Success" if success else "Failed"
        return f"Execution {status}:\n{observation}"
